# Dynatrace AWS Log Forwarder

> ### ⚠️ Dynatrace Log Monitoring and generic log ingest is coming soon. If you are part of the Preview program you can already use dynatrace-aws-log-forwarder to ingest AWS logs. If you are waiting for General Availability please star this repository to get notified when Log Monitoring is ready.

## Overview
This project provides mechanism that allows to stream logs from AWS CloudWatch into Dynatrace Logs via existing ActiveGate. All the necessary AWS infrastructure between those two (Firehose, Lambda, Log Group Subscription Filters) can be deployed and configured by the user through the deployment script provided here (see the *Deployment* section).

### Architecture

CloudWatch Log Groups are subscribed to using Subscription Filters. Their target is Kinesis Data Firehose to which logs are streamed. It aggregates them into batches and sends those batches to a Lambda function for processing. The function processes the received logs and forwards them through Active Gate to Dynatrace Logs API.

Active Gate is required to forward logs to your Dynatrace cluster. You can run it in the same region as the AWS stack or anywhere else as long as you ensure connectivity (especially: open port 9999). In order to install an Active Gate, follow [this instruction](https://www.dynatrace.com/support/help/setup-and-configuration/dynatrace-activegate/installation/install-an-environment-activegate/).

![Architecture](./img/architecture.png)


## Deployment
Deployment can be run from AWS CloudShell or from any machine with AWS CLI installed that supports bash scripts execution (Linux obviously, but also Windows with WSL).

The deployment script uses the default AWS CLI profile configured on the machine. If you want to use a different profile, please [update your configuration file](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-files.html). You can also overwrite the default profile temporarily (limited to your shell session) using [environment variables](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-envvars.html).

### Deploying the infrastructure
Set the following environment variables in your environment:

```
TARGET_URL=https://<active_gate_address>:9999/e/<environment_id>
TARGET_API_TOKEN=dt0c01.ST2<Public portion of token>7YN.G3D<Secret portion of token>RZM
REQUIRE_VALID_CERTIFICATE=false
```

Download the script and deploy the infrastructure:

```
wget -q https://github.com/dynatrace-oss/dynatrace-aws-log-forwarder/releases/latest/download/dynatrace-aws-log-forwarder.zip && unzip -q dynatrace-aws-log-forwarder.zip && cd dynatrace-aws-log-forwarder && ./dynatrace-aws-logs.sh deploy --target-url $TARGET_URL --target-api-token $TARGET_API_TOKEN --require-valid-certificate $REQUIRE_VALID_CERTIFICATE
```

#### Usage and options reference - deploy
```
 dynatrace-aws-logs.sh deploy --target-url TARGET_URL --target-api-token TARGET_API_TOKEN [--require-valid-certificate {true|false}] [--stack-name STACK_NAME]
```

| Command line option  | Environment variable | Description                                | 
| -----------|----------------|---------------------------------------------|
| --target-url | TARGET_URL | The URL to Your Dynatrace SaaS environment logs ingest target. Currently only ActiveGate endpoint is supported:  https://<active_gate_address>:9999/e/<environment_id> (e.g. https://22.111.98.222:9999/e/abc12345) | 
| --target-api-token | TARGET_API_TOKEN | Dynatrace API token. You can learn how to generate token [Dynatrace API - Tokens and authentication](https://www.dynatrace.com/support/help/dynatrace-api/basics/dynatrace-api-authentication) manually. Integration requires `API v1 Log import` Token permission. | 
| --require-valid-certificate | REQUIRE_VALID_CERTIFICATE | *Optional*.Enables checking SSL certificate of the target Active Gate. By default (if this option is not provided) certificates aren't validated |
| --stack-name | STACK_NAME | *Optional*.The name for the CloudFormation stack in which the resources will be deployed. This defaults to *dynatrace-aws-logs* |

## Manage subscribed log groups

### Subscribe to log groups
After deploying the infrastructure, you need to **subscribe** to the log groups you are interested in to forward Logs to the Dynatrace.

#### Subscribe with CLI arguments
```
dynatrace-aws-logs.sh subscribe --log-groups LOG_GROUPS_LIST
```
 The `LOG_GROUPS_LIST` is a space-separated list of log group names you want to subscribe to, e.g. `/aws/lambda/my-lambda /aws/apigateway/my-api`.

#### Subscribe with log groups from file

If you have a large number of log groups you'd like to subscribe to, a more convenient method can be to read them from file. The file should contain each log group name in a separate line and can be provided as:

```
./dynatrace-aws-logs.sh subscribe --log-groups-from-file LOG_GROUPS_FILE
```

#### Log groups autodiscovery

To simplify the file creation we provide the **autodiscovery** option. It lists the names of all the log groups in your account. You can redirect its output to a file and then adjust the list manually before subscribing:

```
./dynatrace-aws-logs.sh discover-log-groups > LOG_GROUPS_FILE
```

#### Subscribing with subscription filter pattern  

By default, AWS subscription filter with a blank filter pattern is created, allowing you to subscribe to all the logs in the log group. 

Alternatively, you can restrict the log you want to subscribe to, using `--filter-pattern` argument. See AWS documentation for allowed [pattern syntax](https://docs.aws.amazon.com/AmazonCloudWatch/latest/logs/FilterAndPatternSyntax.html)

Note, however, that there is a hard AWS limit of 2 subscription filters per each logGroup, limiting the possibility of creating multiple filters with different patterns. If the subscription filter cannot be created because this would exceed the limit, an AWS LimitExceededException will occur.  

```
./dynatrace-aws-logs.sh subscribe --log-groups LOG_GROUPS_LIST --filter-pattern FILTER_PATTERN
```



#### Unsubscribe from log groups

If you don't want to forward logs to Dynatrace anymore, you can **unsubscribe** from log groups in a way similar to subscribing by either passing the log group names as the script parameter:


```
./dynatrace-aws-logs.sh unsubscribe --log-groups LOG_GROUPS_LIST
```

#### Unsubscribe with log groups from file
or using a file containing the log group names:

```
./dynatrace-aws-logs.sh unsubscribe --log-groups-from-file LOG_GROUPS_FILE
```

#### Usage and options reference - subscribe

```
dynatrace-aws-logs.sh subscribe {--log-groups LOG_GROUPS_LIST | --log-groups-from-file LOG_GROUPS_FILE} 
                    [--stack-name STACK_NAME] [--filter-pattern FILTER_PATTERN] [--role-arn ROLE_ARN] [--firehose-arn FIREHOSE_ARN]
```

| Command line option  | Environment variable | Description                                | 
| -----------|----------------|---------------------------------------------|
| --log-groups | LOG_GROUPS_LIST | A space-separated list of log group names you want to subscribe to, e.g. /aws/lambda/my-lambda /aws/apigateway/my-api | 
| --log-groups-from-file | LOG_GROUPS_FILE | The file listing log-groups you want to subscribe to. The file should contain each log group name in a separate line | 
| --stack-name | STACK_NAME | *Optional.* The name of the CloudFormation stack if other than default one (*dynatrace-aws-logs*) has been used in the deploy step |
| --filter-pattern | FILTER_PATTERN | *Optional.* If present, allows subscribing to a filtered stream of logs. If absent, subscribes to all logs in the LogGroup. |
| --role-arn | ROLE_ARN | *Optional.* If not provided, this will be extracted from the Output of CloudFormation stack used in the deploy step, either the default one \"$DEFAULT_STACK_NAME\" or the one specified using --stack-name STACK_NAME option. You can set this option manually if the calls to CloudFormation are a problem due to e.g. permissions or performance reasons. The ARN of the AWS Role that allows creation of SubscriptionFilters. This role is automatically created and its ARN presented as a CloudFormation output of a deploy step of this script. |
| --firehose-arn | FIREHOSE_ARN | *Optional.* If not provided, this will be extracted from the Output of CloudFormation stack used in the deploy step, either the default one \"$DEFAULT_STACK_NAME\" or the one specified using --stack-name STACK_NAME option. You can set this option manually if the calls to CloudFormation are a problem due to e.g. permissions or performance reasons. The ARN of the AWS Kinesis Firehose to stream the logs. This Firehose is automatically created and its ARN presented as a CloudFormation output of a deploy step of this script. |


#### Usage and options reference - unsubscribe
```
 dynatrace-aws-logs.sh unsubscribe {--log-groups LOG_GROUPS_LIST | --log-groups-from-file LOG_GROUPS_FILE} [--stack-name STACK_NAME]
```


| Command line option  | Environment variable | Description                                | 
| -----------|----------------|---------------------------------------------|
| --log-groups | LOG_GROUPS_LIST | A space-separated list of log group names you want to subscribe to, e.g. /aws/lambda/my-lambda /aws/apigateway/my-api | 
| --log-groups-from-file | LOG_GROUPS_FILE | The file listing log-groups you want to subscribe to. The file should contain each log group name in a separate line | 
| --stack-name | STACK_NAME | *Optional.* The name of the CloudFormation stack if other than default one (*dynatrace-aws-logs*) has been used in the deploy step |

