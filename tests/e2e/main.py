#!/usr/bin/env python3

import argparse
from botocore.exceptions import ClientError
import boto3
import time

epoch_timestamp_in_ms = int(time.time() * 1000)

# Create AWS CloudWatch client
aws_client = boto3.client('logs')

def generate_log_event(log_group_name,log_stream_name):
    """
    Upload a log event to the specified AWS CloudWatch Logs log group
    """

    try:
        log_event = aws_client.put_log_events(
            logGroupName  = log_group_name,
            logStreamName = log_stream_name,
            logEvents=[
                {
                    'timestamp': epoch_timestamp_in_ms,
                    'message': 'This is a test log for ' + str(log_group_name)
                },
            ],
        )
        print("Generated log event: %s" % log_event)
    except ClientError as e:
        if e.response['Error']['Code'] == 'DataAlreadyAcceptedException' or e.response['Error']['Code'] == 'InvalidSequenceTokenException':
            print("Given log batch has already been accepeted. Retrying with the following sequence token: " + e.response['expectedSequenceToken'])
            log_event_retry = aws_client.put_log_events(
                logGroupName  = log_group_name,
                logStreamName = log_stream_name,
                logEvents=[
                    {
                        'timestamp': epoch_timestamp_in_ms,
                        'message': 'This is a test log for ' + str(log_group_name)
                    },
                ],
                sequenceToken = e.response['expectedSequenceToken']
            )
            print("Generated log event: %s" % log_event_retry)
        else:
            raise(e)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--log-group-name',
                        '-l',
                        action='store',
                        type=str,
                        default='',
                        required=True,
                        help='specify AWS CloudWatch Logs log group name')
    parser.add_argument('--log-stream-name',
                        '-s',
                        action='store',
                        type=str,
                        default='',
                        required=True,
                        help='specify AWS CloudWatch Logs log stream name for a given log group')
    args = parser.parse_args()

    # Generate a test log event
    generate_log_event(args.log_group_name,args.log_stream_name)