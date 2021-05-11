#!/bin/bash
#   Copyright 2021 Dynatrace LLC
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

readonly TEMPLATE_FILE="dynatrace-aws-log-forwarder-template.yaml"
readonly LAMBDA_ZIP_NAME="dynatrace-aws-log-forwarder-lambda.zip"

readonly DEFAULT_STACK_NAME="dynatrace-aws-logs"

function print_help_main_options {
  echo ""
  printf \
"usage: dynatrace-aws-logs.sh [-h]
                              {deploy,subscribe,unsubscribe,discover-log-groups}
                              ...

optional arguments:
  -h, --help            show this help message and exit

actions:
  valid commands

  {deploy,subscribe,unsubscribe,discover-log-groups}
                        Actions to be executed by the script:
    deploy              Deploy AWS infrastructure (AWS Kinesis Firehose and AWS Lambda) configured to forward logs from AWS CloudWatch to Dynatrace ActiveGate.
    subscribe           Subscribe Dynatrace to Logs from LogGroup(s) (creates a Subscription Filter per each given Log Group)
    unsubscribe         Unsubscribe Dynatrace from Logs from LogGroup(s) (removes Subscription Filter from each given Log Group)
    discover-log-groups Convenience option to list all existing log groups in your AWS account
"

}


if [ $# -eq 0 ]; then echo "No arguments supplied"; print_help_main_options; exit 1; fi

MAIN_OPTION=$1
shift

case $MAIN_OPTION in

"deploy")

  function print_help_deploy {
    printf "
usage: dynatrace-aws-logs.sh deploy --target-url TARGET_URL --target-api-token TARGET_API_TOKEN [--require-valid-certificate {true|false}] [--stack-name STACK_NAME]

arguments:
  -h, --help            show this help message and exit
  --target-url TARGET_URL
                        The URL to Your Dynatrace SaaS environment logs ingest target. Currently only ActiveGate endpoint is supported: https://<active_gate_address>:9999/e/<environment_id> (e.g. https://22.111.98.222:9999/e/abc12345)
  --target-api-token TARGET_API_TOKEN
                        Dynatrace API token. Integration requires API v1 Log import Token permission.
  --require-valid-certificate {true|false}
                        Enables checking SSL certificate of the target Active Gate. By default (if this option is not provided) certificates aren't validated
  --stack-name STACK_NAME
                        Optional. The name for the CloudFormation stack in which the resources will be deployed. This defaults to \"$DEFAULT_STACK_NAME\"
"
  }

  function print_params_deploy {
    echo
    echo "Deployment script will use following parameters:"
    echo "TARGET_URL=\"$TARGET_URL\", TARGET_API_TOKEN=*****, REQUIRE_VALID_CERTIFICATE=\"$REQUIRE_VALID_CERTIFICATE\", STACK_NAME=\"$STACK_NAME\""
  }

  function ensure_param_value_given {
    # Checks if a value ($2) was passed for a parameter ($1). The two OR'ed conditions catch the following mistakes:
    # 1. The parameter is the last one and has no value
    # 2. The parameter is between other parameters and (as it has no value) the name of the next parameter is taken as its value
    if [ -z $2 ] || [[ $2 == "--"* ]]; then echo "Missing value for parameter $1"; print_help_deploy; exit 1; fi
  }

  while (( "$#" )); do
    case "$1" in

      "--target-url")
        ensure_param_value_given $1 $2
        TARGET_URL=$2
        shift; shift
      ;;

      "--target-api-token")
        ensure_param_value_given $1 $2
        TARGET_API_TOKEN=$2
        shift; shift
      ;;

      "--require-valid-certificate")
        ensure_param_value_given $1 $2
        REQUIRE_VALID_CERTIFICATE=$2
        shift; shift
      ;;

      "--stack-name")
        ensure_param_value_given $1 $2
        STACK_NAME=$2
        shift;shift;
      ;;

      "-h")
        print_help_deploy
        shift; exit 0
      ;;
      "--help")
        print_help_deploy
        shift; exit 0
      ;;
      *)
        echo "Unknown param $1"
        print_help_deploy
        exit 1
    esac
  done

  if [ -z "$TARGET_URL" ]; then echo "No --target-url"; print_help_deploy; exit 1; fi
  if [ -z "$TARGET_API_TOKEN" ]; then echo "No --target-api-token"; print_help_deploy; exit 1; fi
  if [ -z "$REQUIRE_VALID_CERTIFICATE" ]; then REQUIRE_VALID_CERTIFICATE="false"; fi
  if [ -z "$STACK_NAME" ]; then STACK_NAME=$DEFAULT_STACK_NAME; fi

  if [[ "$REQUIRE_VALID_CERTIFICATE" != "true" ]] && [[ "$REQUIRE_VALID_CERTIFICATE" != "false" ]];
    then echo "Invalid value for parameter --require-valid-certificate. Provide 'true' or 'false'"; print_help_deploy; exit 1; fi

  print_params_deploy

  set -e

  echo "Deploying stack $STACK_NAME"

  aws cloudformation deploy --stack "$STACK_NAME" --template-file "$TEMPLATE_FILE" --capabilities CAPABILITY_IAM \
    --parameter-overrides DynatraceEnvironmentUrl="$TARGET_URL" DynatraceApiKey="$TARGET_API_TOKEN" VerifySSLTargetActiveGate="$REQUIRE_VALID_CERTIFICATE"

  LAMBDA_ARN=$(aws cloudformation describe-stacks --stack-name "$STACK_NAME" \
     --query "Stacks[0].Outputs[?OutputKey=='LambdaArn'][OutputValue]" --output text)

  aws lambda update-function-code --function-name "$LAMBDA_ARN" --zip-file fileb://"$LAMBDA_ZIP_NAME" > /dev/null

  # SHOW OUTPUTS
  aws cloudformation describe-stacks --stack-name "$STACK_NAME" --query "Stacks[0].Outputs"
  ;;


"subscribe")

  function print_help_subcribe {
    printf "
usage: dynatrace-aws-logs.sh subscribe {--log-groups LOG_GROUPS_LIST [LOG_GROUPS_LIST ...] | --log-groups-from-file LOG_GROUPS_FILE} [--stack-name STACK_NAME]
										[--filter-pattern FILTER_PATTERN] [--role-arn ROLE_ARN] [--firehose-arn FIREHOSE_ARN]

arguments:
  -h, --help            show this help message and exit
  --log-groups LOG_GROUPS_LIST [LOG_GROUPS_LIST ...]
                        A space-separated list of log group names you want to subscribe to, e.g. /aws/lambda/my-lambda /aws/apigateway/my-api
  --log-groups-from-file LOG_GROUPS_FILE
                        The file listing log-groups you want to subscribe to. The file should contain each log group name in a separate line
  --stack-name STACK_NAME
                        Optional. The name of the CloudFormation stack if other than default one \"$DEFAULT_STACK_NAME\" has been used in the deploy step

  --filter-pattern FILTER_PATTERN
                        Optional. If present, allows subscribing to a filtered stream of logs. If absent, subscribes to all logs in the LogGroup.
  --role-arn ROLE_ARN
                        Optional. If not provided, this will be extracted from the Output of CloudFormation stack used in the deploy step, either the default one \"$DEFAULT_STACK_NAME\" or the one specified using --stack-name STACK_NAME option. You can set this option manually if the calls to CloudFormation are a problem due to e.g. permissions or performance reasons.
                        The ARN of the AWS Role that allows creation of SubscriptionFilters. This role is automatically created and its ARN presented as a CloudFormation output of a deploy step of this script.
  --firehose-arn FIREHOSE_ARN
                        Optional. If not provided, this will be extracted from the Output of CloudFormation stack used in the deploy step, either the default one \"$DEFAULT_STACK_NAME\" or the one specified using --stack-name STACK_NAME option. You can set this option manually if the calls to CloudFormation are a problem due to e.g. permissions or performance reasons.
                        The ARN of the AWS Kinesis Firehose to stream the logs. This Firehose is automatically created and its ARN presented as a CloudFormation output of a deploy step of this script.
"
  }

  function print_params_subscribe {
    echo
    echo "Subscribe script will use following parameters:"
    if [ -z "$LOG_GROUPS_FILE" ]; then PARAMETERS="LOG_GROUPS_LIST=\"$LOG_GROUPS_LIST\""; else PARAMETERS="LOG_GROUPS_FILE=\"$LOG_GROUPS_FILE\""; fi
    PARAMETERS+=", STACK_NAME=\"$STACK_NAME\", FILTER_PATTERN=\"$FILTER_PATTERN\", ROLE_ARN=\"$ROLE_ARN\", FIREHOSE_ARN=\"$FIREHOSE_ARN\""
    echo $PARAMETERS; echo
  }

  LOG_GROUPS=()

  while (( "$#" )); do
    case "$1" in

      "--role-arn")
        ROLE_ARN=$2
        shift; shift
      ;;

      "--firehose-arn")
        FIREHOSE_ARN=$2
        shift; shift
      ;;

      "--filter-pattern")
        FILTER_PATTERN=$2
        shift; shift
      ;;

      "--stack-name")
        STACK_NAME=$2
        shift;shift;
      ;;

      "--log-groups")
        shift
        while (( "$#" )); do
          if [[ $1 == "--"* ]]; then
            break
          fi
          LOG_GROUPS+=("$1")
          shift
        LOG_GROUPS_LIST=${LOG_GROUPS[*]}
        done
      ;;

      "--log-groups-from-file")
        set -e
        LOG_GROUPS_FILE=$2
        LOG_GROUPS+=( $(cat $LOG_GROUPS_FILE) )
        set +e
        shift; shift
      ;;

      "-h")
        shift
        print_help_subcribe; exit 0
      ;;
      "--help")
        shift
        print_help_subcribe; exit 0
      ;;
      *)
        echo "Unknown param $1"; print_help_subcribe; exit 1
    esac
  done

  if [ -z "$STACK_NAME" ]; then STACK_NAME=$DEFAULT_STACK_NAME; fi
  SUBSCRIPTION_FILTER_NAME=$STACK_NAME

  if [ -z "$ROLE_ARN" ]; then ROLE_ARN=$(aws cloudformation describe-stacks --stack-name "$STACK_NAME" --query "Stacks[0].Outputs[?OutputKey=='RoleForSubscriptionFiltersArn'].OutputValue | [0]" --output text); fi
  if [ -z "$ROLE_ARN" ]; then echo "No --role-arn"; print_help_subcribe; exit 1; fi
  if [ -z "$FIREHOSE_ARN" ]; then FIREHOSE_ARN=$(aws cloudformation describe-stacks --stack-name "$STACK_NAME" --query "Stacks[0].Outputs[?OutputKey=='FirehoseArn'].OutputValue | [0]" --output text); fi
  if [ -z "$FIREHOSE_ARN" ]; then echo "No --firehose-arn"; print_help_subcribe; exit 1; fi

  if [ "${#LOG_GROUPS[@]}" -lt 1 ]; then LOG_GROUPS=($LOG_GROUPS_LIST); fi
  if [ "${#LOG_GROUPS[@]}" -lt 1 ]; then echo "No Log Groups specified"; print_help_subcribe; exit 1; fi

  if [ -z "$FILTER_PATTERN" ]; then FILTER_PATTERN=' '; fi

  print_params_subscribe

  LOG_GROUPS_TOTAL=0
  LOG_GROUPS_SUCCESSFUL=0

  for LOG_GROUP in "${LOG_GROUPS[@]}"
  do
    echo -n "Subscribing to log group '$LOG_GROUP' "
    ((LOG_GROUPS_TOTAL++))

    aws logs put-subscription-filter --log-group-name "$LOG_GROUP" --filter-name "$SUBSCRIPTION_FILTER_NAME" \
      --filter-pattern "$FILTER_PATTERN" --destination-arn "$FIREHOSE_ARN" --role-arn "$ROLE_ARN"

    RET_VAL=$?
    if [ $RET_VAL -eq 0 ]; then
      echo "SUCCESS"
      ((LOG_GROUPS_SUCCESSFUL++))
    fi
    echo "============="
  done

  echo "$LOG_GROUPS_SUCCESSFUL/$LOG_GROUPS_TOTAL log groups subscribed to successfully"
  ;;


"unsubscribe")

  function print_help_unsubcribe {
    printf "
usage: dynatrace-aws-logs.sh unsubscribe {--log-groups LOG_GROUPS_LIST [LOG_GROUPS_LIST ...] | --log-groups-from-file LOG_GROUPS_FILE} [--stack-name STACK_NAME]

arguments:
  -h, --help            show this help message and exit
  --log-groups LOG_GROUPS_LIST [LOG_GROUPS_LIST ...]
                        A space-separated list of log group names you want to subscribe to, e.g. /aws/lambda/my-lambda /aws/apigateway/my-api
  --log-groups-from-file LOG_GROUPS_FILE
                        The file listing log-groups you want to subscribe to. The file should contain each log group name in a separate line

  --stack-name STACK_NAME
                        Optional. The name of the CloudFormation stack if other than default one \"$DEFAULT_STACK_NAME\" has been used in the deploy step
"
  }

  function print_params_unsubscribe {
    echo
    echo "Unsubscribe script will use following parameters:"
    if [ -z "$LOG_GROUPS_FILE" ]; then PARAMETERS="LOG_GROUPS_LIST=\"$LOG_GROUPS_LIST\""; else PARAMETERS="LOG_GROUPS_FILE=\"$LOG_GROUPS_FILE\""; fi
    echo $PARAMETERS; echo
  }

  LOG_GROUPS=()

  while (( "$#" )); do
    case "$1" in

      "--stack-name")
        STACK_NAME=$2
        shift;shift;
      ;;

      "--log-groups")
        shift
        while (( "$#" )); do
          if [[ $1 == "--"* ]]; then
            break
          fi
          LOG_GROUPS+=("$1")
          shift
        done
        LOG_GROUPS_LIST=${LOG_GROUPS[*]}
      ;;

      "--log-groups-from-file")
        set -e
        LOG_GROUPS_FILE=$2
        LOG_GROUPS+=( $(cat $LOG_GROUPS_FILE) )
        set +e
        shift; shift
      ;;

      "-h")
        print_help_unsubcribe;
        shift; exit 0
      ;;
      "--help")
        print_help_unsubcribe
        shift; exit 0
      ;;
      *)
        echo "Unknown param $1"; print_help_unsubcribe; exit 1
    esac
  done

  if [ -z "$STACK_NAME" ]; then STACK_NAME=$DEFAULT_STACK_NAME; fi
  SUBSCRIPTION_FILTER_NAME=$STACK_NAME

  if [ "${#LOG_GROUPS[@]}" -lt 1 ]; then LOG_GROUPS=($LOG_GROUPS_LIST); fi
  if [ "${#LOG_GROUPS[@]}" -lt 1 ]; then echo "No Log Groups specified"; print_help_unsubcribe; exit 1; fi

  print_params_unsubscribe

  LOG_GROUPS_TOTAL=0
  LOG_GROUPS_SUCCESSFUL=0

  for LOG_GROUP in "${LOG_GROUPS[@]}"
  do
    echo -n "Unsubscribing stack $STACK_NAME from log group '$LOG_GROUP' "
    ((LOG_GROUPS_TOTAL++))

    aws logs delete-subscription-filter --log-group-name "$LOG_GROUP" --filter-name "$SUBSCRIPTION_FILTER_NAME"

    RET_VAL=$?
    if [ $RET_VAL -eq 0 ]; then
      echo "SUCCESS"
      ((LOG_GROUPS_SUCCESSFUL++))
    fi
    echo "============="
  done

  echo "$LOG_GROUPS_SUCCESSFUL/$LOG_GROUPS_TOTAL log groups unsubscribed from successfully"
  ;;


"discover-log-groups")
  function print_help_discover {
    printf "
usage: dynatrace-aws-logs.sh discover-log-groups
"
  }
  while (( "$#" )); do
    case "$1" in
      "-h")
        print_help_discover;
        shift; exit 0
      ;;
      "--help")
        print_help_discover
        shift; exit 0
      ;;
      *)
        echo "Unknown param $1"; print_help_discover; exit 1
    esac
  done
  AWS_PAGER="" aws logs describe-log-groups --output text --query "logGroups[].[logGroupName]"

 ;;

"-h")
   print_help_main_options
 ;;
"--help")
   print_help_main_options
 ;;
*)
  echo "Unknown option" $MAIN_OPTION
  print_help_main_options
  exit 1


esac

