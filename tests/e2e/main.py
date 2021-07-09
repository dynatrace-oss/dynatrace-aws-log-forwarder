#!/usr/bin/env python3

import argparse
from botocore.exceptions import ClientError
import boto3
import time
import requests

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
                    'message': message_content
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
                        'message': message_content
                    },
                ],
                sequenceToken = e.response['expectedSequenceToken']
            )
            print("Generated log event: %s" % log_event_retry)
        else:
            raise(e)

def search_dynatrace_log_records(url_prefix,
                                 message):
    """
    (using Dynatrace API) return a list of log records matching the specified query
    """
    url = url_prefix + '/logs/search?' + 'from=now-5m&limit=1000&query=aws.service%3D%22lambda%22%20AND%20content%3D%22' + message_content + '%22&sort=-timestamp'
    response = requests.get(url,
                            headers=request_headers)

    # check, if response status code is OK
    if response.status_code != requests.codes.ok:
        response.raise_for_status()

    return response.json()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--url-prefix',
                        '-u',
                        action='store',
                        type=str,
                        default='https://jxw01498.dev.dynatracelabs.com/api/v2',
                        help='specify Dynatrace SaaS URL or Dynatrace AG URL')
    parser.add_argument('--api-token',
                        action='store',
                        type=str,
                        default='',
                        required=True,
                        help='specify Dynatrace API Token')
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

    epoch_timestamp_in_ms = int(time.time() * 1000)
    request_headers       = {'Authorization': 'Api-Token ' + args.api_token,
                            'Content-Type': 'application/json',
                            'charset': 'utf-8'}
    message_content       = 'dynatrace-aws-logs-APM-306464'

    # Generate a test log event
    generate_log_event(args.log_group_name,
                       args.log_stream_name)

    time.sleep(60)

    # Search Dynatrace logs for records with specific message content
    print(search_dynatrace_log_records(args.url_prefix,
                                       message_content))