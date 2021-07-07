#!/usr/bin/env python3

import argparse
import boto3

# Create AWS CloudWatch client
aws_client = boto3.client('logs')

def create_log_group(log_group_name,
                     log_group_tags={
                         'app': 'dynatrace',
                         'env': 'develop',
                         'tier': 'monitoring',
                         'cloudformation': 'false',
                     }):
    """
    Create a AWS CloudWatch Logs log group
    """

    aws_client.create_log_group(
        logGroupName = log_group_name,
        tags =         log_group_tags
    )

def delete_log_group(log_group_name):
    """
    Delete a AWS CloudWatch Logs log group
    """

    aws_client.delete_log_group(
        logGroupName = log_group_name
    )

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--log-group-name',
                        '-l',
                        action='store',
                        type=str,
                        default='',
                        required=True,
                        help='specify AWS CloudWatch Logs log group name')
    args = parser.parse_args()

    create_log_group(args.log_group_name)
    delete_log_group(args.log_group_name)