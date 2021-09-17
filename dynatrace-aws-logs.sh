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

readonly DYNATRACE_TARGET_URL_REGEX="^(https?:\/\/[-a-zA-Z0-9@:%._+~=]{1,256}\/?)(\/e\/[a-z0-9-]{36}\/?)?$"
readonly ACTIVE_GATE_TARGET_URL_REGEX="^https:\/\/[-a-zA-Z0-9@:%._+~=]{1,256}\/e\/[-a-z0-9]{1,36}[\/]{0,1}$"

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
    deploy              Deploy AWS log forwarder stack.
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
usage: dynatrace-aws-logs.sh deploy --target-url TARGET_URL --target-api-token TARGET_API_TOKEN --use-existing-active-gate {true|false} [--target-paas-token TARGET_PAAS_TOKEN] [--require-valid-certificate {true|false}] [--stack-name STACK_NAME]

arguments:
  -h, --help            show this help message and exit
  --target-url TARGET_URL
                        The URL to Your Dynatrace SaaS logs ingest target.
                        If you choose new ActiveGate deployment (--use-existing-active-gate=false), provide Tenant URL (https://<your_environment_ID>.live.dynatrace.com).
                        If you choose to use existing ActiveGate (--use-existing-active-gate=true), provide ActiveGate endpoint:
                          - for Public ActiveGate: https://<your_environment_ID>.live.dynatrace.com
                          - for Environment ActiveGate: https://<active_gate_address>:9999/e/<environment_id> (e.g. https://22.111.98.222:9999/e/abc12345)
  --target-api-token TARGET_API_TOKEN
                        Dynatrace API token. Integration requires API v1 Log import Token permission.
  --use-existing-active-gate {true|false}
                        If you choose new ActiveGate deployment, put 'false'. In such case, new EC2 with ActiveGate will be added to log forwarder deployment (enclosed in VPC with log forwarder).
                        If you choose to use existing ActiveGate (either Public AG or Environment AG), put 'true'.
  --target-paas-token TARGET_PAAS_TOKEN
                        Optional. Only needed when --use-existing-active-gate=false. PaaS token generated in Integration/Platform as a Service. Used for ActiveGate installation.
  --require-valid-certificate {true|false}
                        Enables checking SSL certificate of the target Active Gate. By default (if this option is not provided) certificates aren't validated
  --stack-name STACK_NAME
                        Optional. The name for the CloudFormation stack in which the resources will be deployed. This defaults to \"$DEFAULT_STACK_NAME\"
"
  }

  function print_params_deploy {
    echo
    echo "Deployment script will use following parameters:"
    echo "TARGET_URL=\"$TARGET_URL\", TARGET_API_TOKEN=*****, USE_EXISTING_ACTIVE_GATE=\"$USE_EXISTING_ACTIVE_GATE\", TARGET_PAAS_TOKEN=*****, REQUIRE_VALID_CERTIFICATE=\"$REQUIRE_VALID_CERTIFICATE\", STACK_NAME=\"$STACK_NAME\""
  }

  function ensure_param_value_given {
    # Checks if a value ($2) was passed for a parameter ($1). The two OR'ed conditions catch the following mistakes:
    # 1. The parameter is the last one and has no value
    # 2. The parameter is between other parameters and (as it has no value) the name of the next parameter is taken as its value
    if [ -z $2 ] || [[ $2 == "--"* ]]; then echo "Missing value for parameter $1"; print_help_deploy; exit 1; fi
  }

  function check_activegate_state() {
    if ACTIVE_GATE_STATE=$(curl -ksS "${TARGET_URL}/rest/health" --connect-timeout 20); then
      if [[ "$ACTIVE_GATE_STATE" != "RUNNING" ]]
      then
        echo -e ""
        echo -e "\e[91mERROR: \e[37mActiveGate endpoint is not reporting RUNNING state. Please verify provided values for parameter: --target-url (${TARGET_URL})."
        exit 1
      fi
    else
        echo -e "\e[93mWARNING: \e[37mFailed to connect to ActiveGate url $TARGET_URL to check state. It can be ignored if ActiveGate does not allow public access."
    fi
  }

  function check_api_token() {
    if RESPONSE=$(curl -k -s -X POST -d "{\"token\":\"$TARGET_API_TOKEN\"}" "$TARGET_URL/api/v2/apiTokens/lookup" -w "<<HTTP_CODE>>%{http_code}" -H "accept: application/json; charset=utf-8" -H "Content-Type: application/json; charset=utf-8" -H "Authorization: Api-Token $TARGET_API_TOKEN" --connect-timeout 20); then
      CODE=$(sed -rn 's/.*<<HTTP_CODE>>(.*)$/\1/p' <<<"$RESPONSE")
      RESPONSE=$(sed -r 's/(.*)<<HTTP_CODE>>.*$/\1/' <<<"$RESPONSE")
      if [ "$CODE" -ge 300 ]; then
        echo -e "\e[91mERROR: \e[37mFailed to check Dynatrace API token permissions - please verify provided values for parameters: --target-url (${TARGET_URL}) and --target-api-token. $RESPONSE"
        exit 1
      fi
      if ! grep -q '"logs.ingest"' <<<"$RESPONSE"; then
        echo -e "\e[91mERROR: \e[37mMissing Ingest logs permission (v2) for the API token"
        exit 1
      fi
    else
      echo -e "\e[93mWARNING: \e[37mFailed to connect to Dynatrace/ActiveGate endpoint $TARGET_URL to check API token permissions. It can be ignored if Dynatrace/ActiveGate does not allow public access. Please make sure that provided API token has Ingest logs permission (v2)"
    fi
  }

function generate_test_log()
  {
  DATE=$(date --iso-8601=seconds)
  cat <<EOF
{
"timestamp": "$DATE",
"cloud.provider": "aws",
"content": "AWS Log Forwarder installation log",
"severity": "INFO"
}
EOF
  }

  function check_log_ingest_url() {
  if RESPONSE=$(curl -k -s -X POST -d "$(generate_test_log)" "$TARGET_URL/api/v2/logs/ingest" -w "<<HTTP_CODE>>%{http_code}" -H "accept: application/json; charset=utf-8" -H "Content-Type: application/json; charset=utf-8" -H "Authorization: Api-Token $TARGET_API_TOKEN" --connect-timeout 20); then
    CODE=$(sed -rn 's/.*<<HTTP_CODE>>(.*)$/\1/p' <<<"$RESPONSE")
    RESPONSE=$(sed -r 's/(.*)<<HTTP_CODE>>.*$/\1/' <<<"$RESPONSE")
    if [ "$CODE" -ge 300 ]; then
      echo -e "\e[91mERROR: \e[37mFailed to send a test log to Dynatrace - please verify provided log ingest url ($TARGET_URL) and API token. $RESPONSE"
      exit 1
    fi
  else
    echo -e "\e[91mERROR: \e[37mFailed to connect with provided log ingest url ($TARGET_URL) to send a test log. Please check if provided ActiveGate is accessible publicly."
    exit 1
  fi
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

      "--use-existing-active-gate")
        ensure_param_value_given $1 $2
        USE_EXISTING_ACTIVE_GATE=$2
        shift;shift;
      ;;

      "--target-paas-token")
        ensure_param_value_given $1 $2
        TARGET_PAAS_TOKEN=$2
        shift;shift;
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

      "-h" | "--help")
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
  if [ -z "$USE_EXISTING_ACTIVE_GATE" ]; then echo "No --use-existing-active-gate"; print_help_deploy; exit 1; fi

  if [[ "$REQUIRE_VALID_CERTIFICATE" != "true" ]] && [[ "$REQUIRE_VALID_CERTIFICATE" != "false" ]];
    then echo "Invalid value for parameter --require-valid-certificate. Provide 'true' or 'false'"; print_help_deploy; exit 1; fi
  if [[ "$USE_EXISTING_ACTIVE_GATE" != "true" ]] && [[ "$USE_EXISTING_ACTIVE_GATE" != "false" ]];
    then echo "Invalid value for parameter --use-existing-active-gate. Provide 'true' or 'false'"; print_help_deploy; exit 1; fi
  if [[ "$USE_EXISTING_ACTIVE_GATE" == "false" ]] && [ -z "$TARGET_PAAS_TOKEN" ];
    then echo "No --target-paas-token"; print_help_deploy; exit 1; fi

  if [[ "$USE_EXISTING_ACTIVE_GATE" == "false" ]]; then
    # extract tenantID: https://<your_environment_ID>.live.dynatrace.com ==> <your_environment_ID>
    TENANT_ID=$(echo $TARGET_URL | sed 's|https://\([^.]*\).*|\1|')
  else
    TENANT_ID="" # NOT USED IN THIS CASE
  fi

  if [[ "$USE_EXISTING_ACTIVE_GATE" == "false" ]] && ! [[ "${TARGET_URL}" =~ $DYNATRACE_TARGET_URL_REGEX ]]; then
      echo "Invalid value for parameter --target-url. Example of valid url for deployment with new ActiveGate: https://<your_environment_ID>.live.dynatrace.com"
      exit 1
  elif [[ "$USE_EXISTING_ACTIVE_GATE" == "true" ]] && ! ([[ "${TARGET_URL}" =~ $ACTIVE_GATE_TARGET_URL_REGEX ]] || [[ "${TARGET_URL}" =~ $DYNATRACE_TARGET_URL_REGEX ]]); then
      echo "Invalid value for parameter --target-url. Example of valid url for deployment with existing ActiveGate:"
      echo "  - for Public ActiveGate: https://<your_environment_ID>.live.dynatrace.com"
      echo "  - for Environment ActiveGate: https://<your_activegate_IP_or_hostname>:9999/e/<your_environment_ID>"
      exit 1
  fi

  TARGET_URL=$(echo "$TARGET_URL" | sed 's:/*$::')

  if [[ "$USE_EXISTING_ACTIVE_GATE" == "true" ]]; then
    check_activegate_state
  fi

  check_api_token

  if [[ "$USE_EXISTING_ACTIVE_GATE" == "true" ]]; then
    check_log_ingest_url
  fi

  print_params_deploy

  set -e

  echo "Deploying stack $STACK_NAME. This might take up to 10 minutes."

  aws cloudformation deploy --stack "$STACK_NAME" --template-file "$TEMPLATE_FILE" --capabilities CAPABILITY_IAM \
    --parameter-overrides DynatraceEnvironmentUrl="$TARGET_URL" DynatraceApiKey="$TARGET_API_TOKEN" VerifySSLTargetActiveGate="$REQUIRE_VALID_CERTIFICATE" \
    UseExistingActiveGate="$USE_EXISTING_ACTIVE_GATE" TenantId="$TENANT_ID" DynatracePaasToken="$TARGET_PAAS_TOKEN" \
    --no-fail-on-empty-changeset

  LAMBDA_ARN=$(aws cloudformation describe-stacks --stack-name "$STACK_NAME" \
     --query "Stacks[0].Outputs[?OutputKey=='LambdaArn'][OutputValue]" --output text)

  aws lambda update-function-code --function-name "$LAMBDA_ARN" --zip-file fileb://"$LAMBDA_ZIP_NAME" > /dev/null
  echo; echo "Updated Lambda code of $LAMBDA_ARN"; echo

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
                        The ARN of the AWS Role that allows CloudWatch to stream logs to the destination Firehose. This role is automatically created and its ARN presented as a CloudFormation output of a deploy step of this script.
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

      "-h" | "--help")
        shift
        print_help_subcribe; exit 0
      ;;
      *)
        echo "Unknown param $1"; print_help_subcribe; exit 1
    esac
  done

  if [ -z "$STACK_NAME" ]; then STACK_NAME=$DEFAULT_STACK_NAME; fi
  SUBSCRIPTION_FILTER_NAME=$STACK_NAME

  if [ -z "$ROLE_ARN" ]; then ROLE_ARN=$(aws cloudformation describe-stacks --stack-name "$STACK_NAME" --query "Stacks[0].Outputs[?OutputKey=='CloudWatchLogsRoleArn'].OutputValue | [0]" --output text); fi
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
    echo -n "Subscribing stack $STACK_NAME to log group '$LOG_GROUP' "
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

      "-h" | "--help")
        print_help_unsubcribe;
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
      "-h" | "--help")
        print_help_discover;
        shift; exit 0
      ;;
      *)
        echo "Unknown param $1"; print_help_discover; exit 1
    esac
  done
  AWS_PAGER="" aws logs describe-log-groups --output text --query "logGroups[].[logGroupName]"

 ;;

"-h" | "--help")
   print_help_main_options
 ;;
*)
  echo "Unknown option" $MAIN_OPTION
  print_help_main_options
  exit 1


esac

