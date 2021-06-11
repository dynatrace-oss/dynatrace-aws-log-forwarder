# Dynatrace AWS Log Forwarder

## Overview
See the [official project documentation](https://www.dynatrace.com/support/help/technology-support/cloud-platforms/amazon-web-services/aws-log-forwarder/) for overview and user's manual. This readme contains only additional technical details.

### Architecture

CloudWatch Log Groups are subscribed to using Subscription Filters. Their target is Kinesis Data Firehose to which logs are streamed. It aggregates them into batches and sends those batches to a Lambda function for processing. The function processes the received logs and forwards them through Active Gate to Dynatrace Logs API.

Active Gate is required to forward logs to your Dynatrace cluster. You can run it in the same region as the AWS stack or anywhere else as long as you ensure connectivity (especially: open port 9999). In order to install an Active Gate, follow [this instruction](https://www.dynatrace.com/support/help/setup-and-configuration/dynatrace-activegate/installation/install-an-environment-activegate/).

![Architecture](./img/architecture.png)