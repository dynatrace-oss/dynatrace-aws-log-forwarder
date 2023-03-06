#!/usr/bin/env python3

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

import sys
import argparse
from botocore.exceptions import ClientError
import boto3
import time
import requests

# Create AWS CloudWatch client
aws_client = boto3.client('logs')

def generate_log_event(log_group_name,
                       log_stream_name):
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
            print("Given log batch has already been accepted. Retrying with the following sequence token: " + e.response['expectedSequenceToken'])
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
                                 message_content):
    """
    (using Dynatrace API) return a list of log records matching the specified query
    """
    url    = url_prefix + '/logs/search'
    query  = 'content="' + message_content + '"'
    params = {
        'from': 'now-10m',
        'limit': '1000',
        # 'query': 'aws.service%3D%22lambda%22%20AND%20content%3D%22' + message_content + '%22%20AND%20timestamp%3D%22' + str(epoch_timestamp_in_ms) + '%22',
        # 'query': 'timestamp=' + str(epoch_timestamp_in_ms),
        'query': query,
        'sort': '-timestamp'
    }
    response = requests.get(url,
                            headers=request_headers,
                            params=params)

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
    parser.add_argument('--unique-message-content',
                        '-m',
                        action='store',
                        type=str,
                        default='',
                        required=True,
                        help='specify a unique log event message content')
    args = parser.parse_args()

    epoch_timestamp_in_ms = int(time.time() * 1000)
    request_headers       = {'Authorization': 'Api-Token ' + args.api_token,
                            'Content-Type': 'application/json',
                            'charset': 'utf-8'}
    message_content       = args.unique_message_content + '-' + str(epoch_timestamp_in_ms)

    # Generate a test log event
    generate_log_event(args.log_group_name,
                       args.log_stream_name)

    # Search Dynatrace logs for records with specific message content and timestamp
    dynatrace_log_records_search_results = search_dynatrace_log_records(args.url_prefix,
                                                                        message_content)['results']
    time_elapsed = 0
    while bool(dynatrace_log_records_search_results) is False:
        print('Waiting for log events to be picked up by the cluster...')
        time.sleep(60)
        time_elapsed = time_elapsed + 20
        dynatrace_log_records_search_results = search_dynatrace_log_records(args.url_prefix,
                                                                            message_content)['results']
        # Fail the test after 5min
        if time_elapsed == 300:
            print('Generated logs were not found. End-to-end test has failed.')
            sys.exit(1)
            break
    
    print('Generated log events were found. End-to-end test has passed.')
    print("Generated log event found: %s" % dynatrace_log_records_search_results)