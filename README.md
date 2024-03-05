# Dynatrace AWS Log Forwarder

<div align="center">

## ⚠️ **Project Deprecation Notice**

</div>

**Dear users and contributors,**


AWS Log Forwarder will soon be replaced with AWS Data Firehose Integration

**✨ Key Features of the Upcoming Release:**
- 🚀 **Direct Integration:** Ingest cloud logs directly, eliminating the need for extra infrastructure.
- 📈 **Higher Throughput:** Experience increased efficiency with enhanced log forwarding capabilities.
- 🗓️ **Planned Release Date:** Anticipate the official release of Direct AWS Data Firehose Integration at the end of March/April 2024.

**🚨 Important Timeline:**
- 🏷️ **Deprecation Tagging:** Following the release, the current AWS Log Forwarder repository will be tagged as deprecated.
- 📆 **End of Support:** Expect the end of support for the AWS Log Forwarder within the next 6 months post-deprecation.

**👉 What Action Do You Need to Take?**
- ✔️ **Prepare for Transition:** Be ready for the introduction of Direct AWS Data Firehose Integration.
- 📢 **Stay Updated:** Watch for announcements regarding the release and deprecation timeline.
- 🔄 **Plan Migration:** Consider migrating to the new solution to benefit from the latest features and improvements.


**👨‍💻 Questions or Concerns?**
If you have any questions, concerns, or just want to share your thoughts, please reach out.



## Contributing

Please follow these steps:
1. Fork repository and apply your changes.
2. Create a PR to some feature branch in our repo (not to master!)
3. We will review your changes and pull them as our feature branch.
4. Then we will be able to run test pipeline on it, merge to our master and release. 

Thank you! 

## Overview
See the [official project documentation](https://www.dynatrace.com/support/help/shortlink/aws-log-fwd) for overview and user's manual. This readme contains only additional technical details.

### Architecture

CloudWatch Log Groups are subscribed to using Subscription Filters. Their target is Kinesis Data Firehose to which logs are streamed. It aggregates them into batches and sends those batches to a Lambda function for processing. The function processes the received logs and forwards them to Dynatrace Logs API. Alternatively, this last step can be done through an existing environment Active Gate. 

![Architecture](./img/architecture.png)


## Advanced troubleshooting

**Debug EC2 ActiveGate installation**

First, check if ActiveGate is visible in UI (Deployment Status/Active Gates). Right now its label will be EC2's hostname (includes EC2's private IP).

If it is not visible, follow these steps to check AG installation logs:

1. Enable SSH traffic in EC2 Security Group.
2. Connect to EC2 through EC2 Instance Connect in EC2 screen in AWS Console. Use user `ec2-user`. You don't need any SSH keys in this scenario.
3. Check if file `/home/ec2-user/userdata-ag-installation-success` exists. If it does, installation was successful.
4. Check `/var/log/cloud-init-output.log` using sudo. You will find installation script logs there.
