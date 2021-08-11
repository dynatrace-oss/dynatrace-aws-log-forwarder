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

import json
import time

import pytest

import logs.main
import logs.transformation
from logs.models.batch_metadata import BatchMetadata
from util.context import Context

BATCH_METADATA = BatchMetadata("444000444", "us-east-1", "aws")

CLOUDTRAIL_USER_IDENTITY = {
    "type": "AssumedRole",
    "principalId": "AIDA12345667789ABCEF:444000444-somemonitoringuser",
    "arn": "arn:aws:iam::444000444:user/somemonitoringuser",
    "accountId": "444000444",
    "accessKeyId": "AKIA123456789ABCDEFG",
    "sessionContext": {
        "sessionIssuer": {
            "type": "Role",
            "principalId": "AIDA12345667789ABCEF",
            "arn": "arn:aws:iam::444000444:role/sso/dtRoleAdmin",
            "accountId": "444000444",
            "userName": "dtRoleAdmin"
        },
        "webIdFederationData": {},
        "attributes": {
            "mfaAuthenticated": "false",
            "creationDate": "2021-06-21T06:30:44Z"
        }
    }
}

@pytest.mark.parametrize("testcase", [

    pytest.param({
        "record_data_decoded": {
            "logGroup": "API-Gateway-Execution-Logs_8zcb3dxf4l/DEV",
            "logStream": "15ca218e19e3cc840982bd5eef291ac5",
            "messageType": "DATA_MESSAGE",
            "owner": "444000444",
            "subscriptionFilters": ["dynatrace-aws-logs"],
            "logEvents": [
                {
                    "id": "35958590510527767165636549608812769529777864588249006080",
                    "timestamp": "12345",
                    "message": "LOG MESSAGE"
                },
                {
                    "id": "35958590510527767165636549608812769529777864588249006081",
                    "timestamp": "12346",
                    "message": "LOG MESSAGE2"
                },
            ],
        },
        "expect_first_log_contains": {
            "aws.service": "apigateway",
            "aws.resource.id": "8zcb3dxf4l",
            "aws.arn": "arn:aws:apigateway:us-east-1::/restapis/8zcb3dxf4l",
            'content': "LOG MESSAGE",
            'cloud.provider': 'aws',
            'cloud.account.id': "444000444",
            'cloud.region': "us-east-1",
            'aws.log_group': "API-Gateway-Execution-Logs_8zcb3dxf4l/DEV",
            'aws.log_stream': "15ca218e19e3cc840982bd5eef291ac5",
            'aws.region': "us-east-1",
            'aws.account.id': "444000444",
            'severity': 'INFO',
        },
    }, id="testcase_ApiGatewayExecutionLog"),

    pytest.param({
        "record_data_decoded": {
            "logGroup": "/aws/lambda/dynatrace-aws-logs-Lambda-1K7HG2Q2LIQKU",
            "logStream": "15ca218e19e3cc840982bd5eef291ac5",
            "messageType": "DATA_MESSAGE",
            "owner": "444000444",
            "subscriptionFilters": ["dynatrace-aws-logs"],
            "logEvents": [
                {
                    "id": "35958590510527767165636549608812769529777864588249006080",
                    "timestamp": "12345",
                    "message": "LOG MESSAGE"
                },
                {
                    "id": "35958590510527767165636549608812769529777864588249006081",
                    "timestamp": "12346",
                    "message": "LOG MESSAGE2"
                },
            ],
        },
        "expect_first_log_contains": {
            "aws.service": "lambda",
            "aws.resource.id": "dynatrace-aws-logs-Lambda-1K7HG2Q2LIQKU",
            "aws.arn": "arn:aws:lambda:us-east-1:444000444:function:dynatrace-aws-logs-Lambda-1K7HG2Q2LIQKU",
            "dt.source_entity": "AWS_LAMBDA_FUNCTION-F141CAEAE2BED565",
            'content': "LOG MESSAGE",
            'cloud.provider': 'aws',
            'cloud.account.id': "444000444",
            'cloud.region': "us-east-1",
            'aws.log_group': "/aws/lambda/dynatrace-aws-logs-Lambda-1K7HG2Q2LIQKU",
            'aws.log_stream': "15ca218e19e3cc840982bd5eef291ac5",
            'aws.region': "us-east-1",
            'aws.account.id': "444000444",
            'severity': 'INFO',
        }
    }, id="testcase_Lambda"),

    pytest.param({
        "record_data_decoded": {
            "logGroup": "/aws/lambda/dynatrace-aws-logs-Lambda-1K7HG2Q2LIQKU",
            "logStream": "15ca218e19e3cc840982bd5eef291ac5",
            "messageType": "DATA_MESSAGE",
            "owner": "444000444",
            "subscriptionFilters": ["dynatrace-aws-logs"],
            "logEvents": [
                {
                    "id": "35958590510527767165636549608812769529777864588249006080",
                    "timestamp": "12345",
                    "message": "[ERROR] UnboundLocalError: local variable 'single_log_entry' referenced before assignment\n"
                               + "Traceback (most recent call last):\n"
                               + "  File \"/var/task/lambda_function.py\", line 101, in lambda_handler\n"
                               + "    print(i.__str__() + single_log_entry)"
                }
            ],
        },
        "expect_first_log_contains": {
            "aws.service": "lambda",
            "aws.resource.id": "dynatrace-aws-logs-Lambda-1K7HG2Q2LIQKU",
            "aws.arn": "arn:aws:lambda:us-east-1:444000444:function:dynatrace-aws-logs-Lambda-1K7HG2Q2LIQKU",
            "dt.source_entity": "AWS_LAMBDA_FUNCTION-F141CAEAE2BED565",
            'content': "[ERROR] UnboundLocalError: local variable 'single_log_entry' referenced before assignment\n"
                       + "Traceback (most recent call last):\n"
                       + "  File \"/var/task/lambda_function.py\", line 101, in lambda_handler\n"
                       + "    print(i.__str__() + single_log_entry)",
            'cloud.provider': 'aws',
            'cloud.account.id': "444000444",
            'cloud.region': "us-east-1",
            'aws.log_group': "/aws/lambda/dynatrace-aws-logs-Lambda-1K7HG2Q2LIQKU",
            'aws.log_stream': "15ca218e19e3cc840982bd5eef291ac5",
            'aws.region': "us-east-1",
            'aws.account.id': "444000444",
            'severity': 'ERROR',
        }
    }, id="testcase_Lambda_error"),

    pytest.param({
        "record_data_decoded": {"messageType": "DATA_MESSAGE", "owner": "444000444",
                                "logGroup": "aws-cloudtrail-logs-444000444-1cceb782",
                                "logStream": "444000444_CloudTrail_us-east-1",
                                "subscriptionFilters": ["Belu-APM-299389-cloudtrail-RDS_subscriptionFilter"],
                                "logEvents": [{"id": "36184182057683330175263108764349521965726085205046394887",
                                               "timestamp": 1622554840009,
                                               "message": json.dumps({
                                                   "eventVersion": "1.08",
                                                   "userIdentity": CLOUDTRAIL_USER_IDENTITY,
                                                   "eventTime": "2021-05-28T11:39:33Z",
                                                   "eventSource": "rds.amazonaws.com",
                                                   "eventName": "DescribeEvents",
                                                   "awsRegion": "ap-southeast-2",
                                                   "sourceIPAddress": "155.55.55.055",
                                                   "userAgent": "aws-sdk-java/1.11.789 Linux/5.4.0-56-generic OpenJDK_64-Bit_Server_VM/11.0.8+10 java/11.0.8 vendor/AdoptOpenJDK",
                                                   "requestParameters": {
                                                       "startTime": "May 28, 2021 11:29:00 AM",
                                                       "endTime": "May 28, 2021 11:34:00 AM"
                                                   },
                                                   "responseElements": None,
                                                   "requestID": "69de2278-ef7a-4b9a-bdc5-a78c9210ea4e",
                                                   "eventID": "249491df-4970-421d-8575-5bf555357c14",
                                                   "readOnly": True,
                                                   "eventType": "AwsApiCall",
                                                   "managementEvent": True,
                                                   "eventCategory": "Management",
                                                   "recipientAccountId": "444000444"
                                               })
                                               }
                                              ]},
        "expect_first_log_contains": {
            'aws.service': 'cloudtrail',
            'content': '{"eventVersion": "1.08", "userIdentity": {"type": "AssumedRole", "principalId": "AIDA12345667789ABCEF:444000444-somemonitoringuser", "arn": "arn:aws:iam::444000444:user/somemonitoringuser", "accountId": "444000444", "accessKeyId": "AKIA123456789ABCDEFG", "sessionContext": {"sessionIssuer": {"type": "Role", "principalId": "AIDA12345667789ABCEF", "arn": "arn:aws:iam::444000444:role/sso/dtRoleAdmin", "accountId": "444000444", "userName": "dtRoleAdmin"}, "webIdFederationData": {}, "attributes": {"mfaAuthenticated": "false", "creationDate": "2021-06-21T06:30:44Z"}}}, "eventTime": "2021-05-28T11:39:33Z", "eventSource": "rds.amazonaws.com", "eventName": "DescribeEvents", "awsRegion": "ap-southeast-2", "sourceIPAddress": "155.55.55.055", "userAgent": "aws-sdk-java/1.11.789 Linux/5.4.0-56-generic OpenJDK_64-Bit_Server_VM/11.0.8+10 java/11.0.8 vendor/AdoptOpenJDK", "requestParameters": {"startTime": "May 28, 2021 11:29:00 AM", "endTime": "May 28, 2021 11:34:00 AM"}, "responseElements": null, "requestID": "69de2278-ef7a-4b9a-bdc5-a78c9210ea4e", "eventID": "249491df-4970-421d-8575-5bf555357c14", "readOnly": true, "eventType": "AwsApiCall", "managementEvent": true, "eventCategory": "Management", "recipientAccountId": "444000444"}',
            'cloud.provider': 'aws',
            'cloud.account.id': '444000444',
            'cloud.region': 'us-east-1',
            'aws.log_group': 'aws-cloudtrail-logs-444000444-1cceb782',
            'aws.log_stream': '444000444_CloudTrail_us-east-1',
            'aws.region': 'us-east-1',
            'aws.account.id': '444000444',
            'severity': 'INFO',
            'timestamp': 1622554840009,
            'audit.action': 'DescribeEvents',
            'audit.identity': 'arn:aws:iam::444000444:user/somemonitoringuser',
            'audit.result': 'Succeeded'}
    }, id="testcase_Cloudtrail_RDS_DescribeEvents"),

    pytest.param({
        "record_data_decoded": {"messageType": "DATA_MESSAGE", "owner": "444000444",
                                "logGroup": "aws-cloudtrail-logs-444000444-1cceb782",
                                "logStream": "444000444_CloudTrail_us-east-1",
                                "subscriptionFilters": ["Belu-APM-299389-cloudtrail-RDS_subscriptionFilter"],
                                "logEvents": [{"id": "36184182057683330175263108764349521965726085205046394887",
                                               "timestamp": 1622554840009,
                                               "message": json.dumps({
                                                   "eventVersion": "1.08",
                                                   "userIdentity": CLOUDTRAIL_USER_IDENTITY,
                                                   "eventTime": "2021-06-21T07:15:43Z",
                                                   "eventSource": "rds.amazonaws.com",
                                                   "eventName": "ModifyDBCluster",
                                                   "awsRegion": "us-east-1",
                                                   "sourceIPAddress": "157.25.19.100",
                                                   "userAgent": "aws-internal/3 aws-sdk-java/1.11.975 Linux/4.9.230-0.1.ac.224.84.332.metal1.x86_64 OpenJDK_64-Bit_Server_VM/25.242-b08 java/1.8.0_242 vendor/Oracle_Corporation cfg/retry-mode/legacy",
                                                   "errorCode": "InvalidDBClusterStateFault",
                                                   "errorMessage": "DB cluster is not available for modification with status configuring-iam-database-auth",
                                                   "requestParameters": {
                                                       "applyImmediately": True,
                                                       "dBClusterIdentifier": "belu-metadata-database-1",
                                                       "allowMajorVersionUpgrade": False
                                                   },
                                                   "responseElements": None,
                                                   "requestID": "f8a1ee03-1d27-41c7-9b6f-2aafed555986",
                                                   "eventID": "2c230775-64c2-4b82-bb20-24a1effb73bd",
                                                   "readOnly": False,
                                                   "eventType": "AwsApiCall",
                                                   "managementEvent": True,
                                                   "eventCategory": "Management",
                                                   "recipientAccountId": "444000444"
                                               })
                                               }
                                              ]},
        "expect_first_log_contains": {
            'aws.service': 'cloudtrail',
            # "aws.resource.id": "belu-metadata-database-1",
            # "aws.arn": "arn:aws:rds:us-east-1:444000444:cluster:belu-metadata-database-1",
            # "dt.source_entity": "CUSTOM_DEVICE-F033DECA180883EE",
            'content': '{"eventVersion": "1.08", "userIdentity": {"type": "AssumedRole", "principalId": "AIDA12345667789ABCEF:444000444-somemonitoringuser", "arn": "arn:aws:iam::444000444:user/somemonitoringuser", "accountId": "444000444", "accessKeyId": "AKIA123456789ABCDEFG", "sessionContext": {"sessionIssuer": {"type": "Role", "principalId": "AIDA12345667789ABCEF", "arn": "arn:aws:iam::444000444:role/sso/dtRoleAdmin", "accountId": "444000444", "userName": "dtRoleAdmin"}, "webIdFederationData": {}, "attributes": {"mfaAuthenticated": "false", "creationDate": "2021-06-21T06:30:44Z"}}}, "eventTime": "2021-06-21T07:15:43Z", "eventSource": "rds.amazonaws.com", "eventName": "ModifyDBCluster", "awsRegion": "us-east-1", "sourceIPAddress": "157.25.19.100", "userAgent": "aws-internal/3 aws-sdk-java/1.11.975 Linux/4.9.230-0.1.ac.224.84.332.metal1.x86_64 OpenJDK_64-Bit_Server_VM/25.242-b08 java/1.8.0_242 vendor/Oracle_Corporation cfg/retry-mode/legacy", "errorCode": "InvalidDBClusterStateFault", "errorMessage": "DB cluster is not available for modification with status configuring-iam-database-auth", "requestParameters": {"applyImmediately": true, "dBClusterIdentifier": "belu-metadata-database-1", "allowMajorVersionUpgrade": false}, "responseElements": null, "requestID": "f8a1ee03-1d27-41c7-9b6f-2aafed555986", "eventID": "2c230775-64c2-4b82-bb20-24a1effb73bd", "readOnly": false, "eventType": "AwsApiCall", "managementEvent": true, "eventCategory": "Management", "recipientAccountId": "444000444"}',
            'cloud.provider': 'aws',
            'cloud.account.id': '444000444',
            'cloud.region': 'us-east-1',
            'aws.log_group': 'aws-cloudtrail-logs-444000444-1cceb782',
            'aws.log_stream': '444000444_CloudTrail_us-east-1',
            'aws.region': 'us-east-1',
            'aws.account.id': '444000444',
            'severity': 'ERROR',
            'timestamp': 1622554840009,
            'audit.action': 'ModifyDBCluster',
            'audit.identity': 'arn:aws:iam::444000444:user/somemonitoringuser',
            'audit.result': 'Failed.InvalidDBClusterStateFault'}
    }, id="testcase_Cloudtrail_RDS_ModifyDBCluster_error"),


    pytest.param({
        "record_data_decoded": {"messageType": "DATA_MESSAGE", "owner": "444000444",
                                "logGroup": "aws-cloudtrail-logs-444000444-1cceb782",
                                "logStream": "444000444_CloudTrail_us-east-1",
                                "subscriptionFilters": ["Belu-APM-299389-cloudtrail-RDS_subscriptionFilter"],
                                "logEvents": [{"id": "36184182057683330175263108764349521965726085205046394887",
                                               "timestamp": 1622554840009,
                                               "message": json.dumps({
                                                   "eventVersion": "1.08",
                                                   "userIdentity": CLOUDTRAIL_USER_IDENTITY,
                                                   "eventTime": "2021-05-28T12:03:24Z",
                                                   "eventSource": "rds.amazonaws.com",
                                                   "eventName": "DescribeDBClusters",
                                                   "awsRegion": "us-east-1",
                                                   "sourceIPAddress": "188.147.123.198",
                                                   "userAgent": "aws-internal/3 aws-sdk-java/1.11.975 Linux/4.9.230-0.1.ac.224.84.332.metal1.x86_64 OpenJDK_64-Bit_Server_VM/25.242-b08 java/1.8.0_242 vendor/Oracle_Corporation cfg/retry-mode/legacy",
                                                   "requestParameters": {
                                                       "includeShared": True
                                                   },
                                                   "responseElements": None,
                                                   "requestID": "c78e8786-693b-4874-99ad-5f12e31b51aa",
                                                   "eventID": "2e619293-cff3-4d72-b7a0-5768a566b661",
                                                   "readOnly": True,
                                                   "eventType": "AwsApiCall",
                                                   "managementEvent": True,
                                                   "eventCategory": "Management",
                                                   "recipientAccountId": "444000444"
                                               })
                                               }
                                              ]},
        "expect_first_log_contains": {
            'aws.service': 'cloudtrail',
            # "aws.resource.id": None,
            # "aws.arn": None,
            # "dt.source_entity": None,
            'content': '{"eventVersion": "1.08", "userIdentity": {"type": "AssumedRole", "principalId": "AIDA12345667789ABCEF:444000444-somemonitoringuser", "arn": "arn:aws:iam::444000444:user/somemonitoringuser", "accountId": "444000444", "accessKeyId": "AKIA123456789ABCDEFG", "sessionContext": {"sessionIssuer": {"type": "Role", "principalId": "AIDA12345667789ABCEF", "arn": "arn:aws:iam::444000444:role/sso/dtRoleAdmin", "accountId": "444000444", "userName": "dtRoleAdmin"}, "webIdFederationData": {}, "attributes": {"mfaAuthenticated": "false", "creationDate": "2021-06-21T06:30:44Z"}}}, "eventTime": "2021-05-28T12:03:24Z", "eventSource": "rds.amazonaws.com", "eventName": "DescribeDBClusters", "awsRegion": "us-east-1", "sourceIPAddress": "188.147.123.198", "userAgent": "aws-internal/3 aws-sdk-java/1.11.975 Linux/4.9.230-0.1.ac.224.84.332.metal1.x86_64 OpenJDK_64-Bit_Server_VM/25.242-b08 java/1.8.0_242 vendor/Oracle_Corporation cfg/retry-mode/legacy", "requestParameters": {"includeShared": true}, "responseElements": null, "requestID": "c78e8786-693b-4874-99ad-5f12e31b51aa", "eventID": "2e619293-cff3-4d72-b7a0-5768a566b661", "readOnly": true, "eventType": "AwsApiCall", "managementEvent": true, "eventCategory": "Management", "recipientAccountId": "444000444"}',
            'cloud.provider': 'aws',
            'cloud.account.id': '444000444',
            'cloud.region': 'us-east-1',
            'aws.log_group': 'aws-cloudtrail-logs-444000444-1cceb782',
            'aws.log_stream': '444000444_CloudTrail_us-east-1',
            'aws.region': 'us-east-1',
            'aws.account.id': '444000444',
            'severity': 'INFO',
            'timestamp': 1622554840009,
            'audit.action': 'DescribeDBClusters',
            'audit.identity': 'arn:aws:iam::444000444:user/somemonitoringuser',
            'audit.result': 'Succeeded'}
    }, id="testcase_Cloudtrail_RDS_DescribeDBClusters_optional_entity_linking"),

    pytest.param({
        "record_data_decoded": {"messageType": "DATA_MESSAGE", "owner": "444000444",
                                "logGroup": "aws-cloudtrail-logs-444000444-1cceb782",
                                "logStream": "444000444_CloudTrail_us-east-1",
                                "subscriptionFilters": ["Belu-APM-299389-cloudtrail-RDS_subscriptionFilter"],
                                "logEvents": [{"id": "36184182057683330175263108764349521965726085205046394887",
                                               "timestamp": 1622554840009,
                                               "message": json.dumps({
                                                   "eventVersion": "1.08",
                                                   "userIdentity": CLOUDTRAIL_USER_IDENTITY,
                                                   "eventTime": "2021-05-28T12:03:24Z",
                                                   "eventSource": "rds.amazonaws.com",
                                                   "eventName": "ListTagsForResource",
                                                   "awsRegion": "us-east-1",
                                                   "sourceIPAddress": "157.25.19.100",
                                                   "userAgent": "aws-sdk-java/1.11.789 Linux/5.4.0-51-generic OpenJDK_64-Bit_Server_VM/11.0.10+9 java/11.0.10 vendor/AdoptOpenJDK",
                                                   "requestParameters": {
                                                       "resourceName": "arn:aws:rds:us-east-1:444000444:db:belu-metadata-database-1-instance-1"
                                                   },
                                                   "responseElements": None,
                                                   "requestID": "c78e8786-693b-4874-99ad-5f12e31b51aa",
                                                   "eventID": "2e619293-cff3-4d72-b7a0-5768a566b661",
                                                   "readOnly": True,
                                                   "eventType": "AwsApiCall",
                                                   "managementEvent": True,
                                                   "eventCategory": "Management",
                                                   "recipientAccountId": "444000444"
                                               })
                                               }
                                              ]},
        "expect_first_log_contains": {
            'aws.service': 'cloudtrail',
            # "aws.resource.id": 'belu-metadata-database-1-instance-1',
            # "aws.arn": 'arn:aws:rds:us-east-1:444000444:db:belu-metadata-database-1-instance-1',
            # "dt.source_entity": 'RELATIONAL_DATABASE_SERVICE-BD5D6EC7B9C3C4A1',
            'content': '{"eventVersion": "1.08", "userIdentity": {"type": "AssumedRole", "principalId": "AIDA12345667789ABCEF:444000444-somemonitoringuser", "arn": "arn:aws:iam::444000444:user/somemonitoringuser", "accountId": "444000444", "accessKeyId": "AKIA123456789ABCDEFG", "sessionContext": {"sessionIssuer": {"type": "Role", "principalId": "AIDA12345667789ABCEF", "arn": "arn:aws:iam::444000444:role/sso/dtRoleAdmin", "accountId": "444000444", "userName": "dtRoleAdmin"}, "webIdFederationData": {}, "attributes": {"mfaAuthenticated": "false", "creationDate": "2021-06-21T06:30:44Z"}}}, "eventTime": "2021-05-28T12:03:24Z", "eventSource": "rds.amazonaws.com", "eventName": "ListTagsForResource", "awsRegion": "us-east-1", "sourceIPAddress": "157.25.19.100", "userAgent": "aws-sdk-java/1.11.789 Linux/5.4.0-51-generic OpenJDK_64-Bit_Server_VM/11.0.10+9 java/11.0.10 vendor/AdoptOpenJDK", "requestParameters": {"resourceName": "arn:aws:rds:us-east-1:444000444:db:belu-metadata-database-1-instance-1"}, "responseElements": null, "requestID": "c78e8786-693b-4874-99ad-5f12e31b51aa", "eventID": "2e619293-cff3-4d72-b7a0-5768a566b661", "readOnly": true, "eventType": "AwsApiCall", "managementEvent": true, "eventCategory": "Management", "recipientAccountId": "444000444"}',
            'cloud.provider': 'aws',
            'cloud.account.id': '444000444',
            'cloud.region': 'us-east-1',
            'aws.log_group': 'aws-cloudtrail-logs-444000444-1cceb782',
            'aws.log_stream': '444000444_CloudTrail_us-east-1',
            'aws.region': 'us-east-1',
            'aws.account.id': '444000444',
            'severity': 'INFO',
            'timestamp': 1622554840009,
            'audit.action': 'ListTagsForResource',
            'audit.identity': 'arn:aws:iam::444000444:user/somemonitoringuser',
            'audit.result': 'Succeeded'}
    }, id="testcase_Cloudtrail_RDS_ListTagsForResource_resource_id_from_arn"),

    pytest.param({
        "record_data_decoded": {"messageType": "DATA_MESSAGE", "owner": "444000444",
                                "logGroup": "aws-cloudtrail-logs-444000444-1cceb782",
                                "logStream": "444000444_CloudTrail_us-east-1",
                                "subscriptionFilters": ["Belu-APM-299389-cloudtrail-RDS_subscriptionFilter"],
                                "logEvents": [{"id": "36184182057683330175263108764349521965726085205046394887",
                                               "timestamp": 1622554840009,
                                               "message": json.dumps({
                                                   "eventVersion": "1.08",
                                                   "userIdentity": CLOUDTRAIL_USER_IDENTITY,
                                                   "eventTime": "2021-05-28T12:03:24Z",
                                                   "eventSource": "rds.amazonaws.com",
                                                   "eventName": "RegisterDBProxyTargets",
                                                   "awsRegion": "us-east-1",
                                                   "sourceIPAddress": "rds.amazonaws.com",
                                                   "userAgent": "rds.amazonaws.com",
                                                   "requestParameters": {
                                                       "dBProxyName": "beluTestRDSProxy",
                                                       "dBClusterIdentifiers": [
                                                           "belu-metadata-database-1"
                                                       ]
                                                   },
                                                   "responseElements": {
                                                       "dBProxyTargets": [
                                                           {
                                                               "rdsResourceId": "belu-metadata-database-1",
                                                               "port": 5432,
                                                               "type": "TRACKED_CLUSTER",
                                                               "targetHealth": {
                                                                   "state": "REGISTERING"
                                                               }
                                                           },
                                                           {
                                                               "endpoint": "belu-metadata-database-1-instance-1.cx6dmgg4ljp5.us-east-1.rds.amazonaws.com",
                                                               "rdsResourceId": "belu-metadata-database-1-instance-1",
                                                               "port": 5432,
                                                               "type": "RDS_INSTANCE",
                                                               "targetHealth": {
                                                                   "state": "REGISTERING"
                                                               }
                                                           }
                                                       ]
                                                   },
                                                   "requestID": "ca8dd6f5-8752-4eb0-acfe-34c2f0cfc34d",
                                                   "eventID": "7744cfe9-179b-4b49-8475-06c5aa97c391",
                                                   "readOnly": False,
                                                   "eventType": "AwsApiCall",
                                                   "managementEvent": True,
                                                   "eventCategory": "Management",
                                                   "recipientAccountId": "444000444"
                                               })
                                               }
                                              ]},
        "expect_first_log_contains": {
            'aws.service': 'cloudtrail',
            # "aws.resource.id": 'belu-metadata-database-1',
            # "aws.arn": 'arn:aws:rds:us-east-1:444000444:cluster:belu-metadata-database-1',
            # "dt.source_entity": 'CUSTOM_DEVICE-F033DECA180883EE',
            'content': '{"eventVersion": "1.08", "userIdentity": {"type": "AssumedRole", "principalId": "AIDA12345667789ABCEF:444000444-somemonitoringuser", "arn": "arn:aws:iam::444000444:user/somemonitoringuser", "accountId": "444000444", "accessKeyId": "AKIA123456789ABCDEFG", "sessionContext": {"sessionIssuer": {"type": "Role", "principalId": "AIDA12345667789ABCEF", "arn": "arn:aws:iam::444000444:role/sso/dtRoleAdmin", "accountId": "444000444", "userName": "dtRoleAdmin"}, "webIdFederationData": {}, "attributes": {"mfaAuthenticated": "false", "creationDate": "2021-06-21T06:30:44Z"}}}, "eventTime": "2021-05-28T12:03:24Z", "eventSource": "rds.amazonaws.com", "eventName": "RegisterDBProxyTargets", "awsRegion": "us-east-1", "sourceIPAddress": "rds.amazonaws.com", "userAgent": "rds.amazonaws.com", "requestParameters": {"dBProxyName": "beluTestRDSProxy", "dBClusterIdentifiers": ["belu-metadata-database-1"]}, "responseElements": {"dBProxyTargets": [{"rdsResourceId": "belu-metadata-database-1", "port": 5432, "type": "TRACKED_CLUSTER", "targetHealth": {"state": "REGISTERING"}}, {"endpoint": "belu-metadata-database-1-instance-1.cx6dmgg4ljp5.us-east-1.rds.amazonaws.com", "rdsResourceId": "belu-metadata-database-1-instance-1", "port": 5432, "type": "RDS_INSTANCE", "targetHealth": {"state": "REGISTERING"}}]}, "requestID": "ca8dd6f5-8752-4eb0-acfe-34c2f0cfc34d", "eventID": "7744cfe9-179b-4b49-8475-06c5aa97c391", "readOnly": false, "eventType": "AwsApiCall", "managementEvent": true, "eventCategory": "Management", "recipientAccountId": "444000444"}',
            'cloud.provider': 'aws',
            'cloud.account.id': '444000444',
            'cloud.region': 'us-east-1',
            'aws.log_group': 'aws-cloudtrail-logs-444000444-1cceb782',
            'aws.log_stream': '444000444_CloudTrail_us-east-1',
            'aws.region': 'us-east-1',
            'aws.account.id': '444000444',
            'severity': 'INFO',
            'timestamp': 1622554840009,
            'audit.action': 'RegisterDBProxyTargets',
            'audit.identity': 'arn:aws:iam::444000444:user/somemonitoringuser',
            'audit.result': 'Succeeded'}
    }, id="testcase_Cloudtrail_RDS_RegisterDBProxyTargets_multiple_resources"),

    pytest.param({
        "record_data_decoded": {"messageType": "DATA_MESSAGE", "owner": "444000444",
                                "logGroup": "aws-cloudtrail-logs-444000444-1cceb782",
                                "logStream": "444000444_CloudTrail_us-east-1",
                                "subscriptionFilters": ["Belu-APM-299389-cloudtrail-RDS_subscriptionFilter"],
                                "logEvents": [{"id": "36184182057683330175263108764349521965726085205046394887",
                                               "timestamp": 1622554840009,
                                               "message": json.dumps({
                                                   "eventVersion": "1.08",
                                                   "userIdentity": CLOUDTRAIL_USER_IDENTITY,
                                                   "eventTime": "2021-05-28T12:03:24Z",
                                                   "eventSource": "rds.amazonaws.com",
                                                   "eventName": "CreateEventSubscription",
                                                   "awsRegion": "us-east-1",
                                                   "sourceIPAddress": "83.164.160.102",
                                                   "userAgent": "aws-internal/3 aws-sdk-java/1.11.975 Linux/4.9.230-0.1.ac.224.84.332.metal1.x86_64 OpenJDK_64-Bit_Server_VM/25.242-b08 java/1.8.0_242 vendor/Oracle_Corporation cfg/retry-mode/legacy",
                                                   "requestParameters": {
                                                       "subscriptionName": "beluRdsEventSubscription",
                                                       "snsTopicArn": "arn:aws:sns:us-east-1:444000444:test",
                                                       "sourceType": "db-instance",
                                                       "sourceIds": [
                                                           "belu-metadata-database-1-instance-1",
                                                           "belu-mysql-database-1"
                                                       ]
                                                   },
                                                   "responseElements": {
                                                       "customerAwsId": "444000444",
                                                       "custSubscriptionId": "beluRdsEventSubscription",
                                                       "snsTopicArn": "arn:aws:sns:us-east-1:444000444:test",
                                                       "status": "active",
                                                       "subscriptionCreationTime": "Tue Jun 29 12:21:35 UTC 2021",
                                                       "sourceType": "db-instance",
                                                       "sourceIdsList": [
                                                           "belu-metadata-database-1-instance-1",
                                                           "belu-mysql-database-1"
                                                       ],
                                                       "enabled": True,
                                                       "eventSubscriptionArn": "arn:aws:rds:us-east-1:444000444:es:beluRdsEventSubscription"
                                                   },
                                                   "requestID": "b7ef566c-d266-446a-a617-9ddff87cafd7",
                                                   "eventID": "941338b4-bc46-4b2f-8b7e-9149fcf23bb7",
                                                   "readOnly": False,
                                                   "eventType": "AwsApiCall",
                                                   "managementEvent": True,
                                                   "eventCategory": "Management",
                                                   "recipientAccountId": "444000444"
                                               })
                                               }
                                              ]},
        "expect_first_log_contains": {
            'aws.service': 'cloudtrail',
            # "aws.resource.id": 'belu-metadata-database-1-instance-1',
            # "aws.arn": 'arn:aws:rds:us-east-1:444000444:db:belu-metadata-database-1-instance-1',
            # "dt.source_entity": 'RELATIONAL_DATABASE_SERVICE-BD5D6EC7B9C3C4A1',
            'content': '{"eventVersion": "1.08", "userIdentity": {"type": "AssumedRole", "principalId": "AIDA12345667789ABCEF:444000444-somemonitoringuser", "arn": "arn:aws:iam::444000444:user/somemonitoringuser", "accountId": "444000444", "accessKeyId": "AKIA123456789ABCDEFG", "sessionContext": {"sessionIssuer": {"type": "Role", "principalId": "AIDA12345667789ABCEF", "arn": "arn:aws:iam::444000444:role/sso/dtRoleAdmin", "accountId": "444000444", "userName": "dtRoleAdmin"}, "webIdFederationData": {}, "attributes": {"mfaAuthenticated": "false", "creationDate": "2021-06-21T06:30:44Z"}}}, "eventTime": "2021-05-28T12:03:24Z", "eventSource": "rds.amazonaws.com", "eventName": "CreateEventSubscription", "awsRegion": "us-east-1", "sourceIPAddress": "83.164.160.102", "userAgent": "aws-internal/3 aws-sdk-java/1.11.975 Linux/4.9.230-0.1.ac.224.84.332.metal1.x86_64 OpenJDK_64-Bit_Server_VM/25.242-b08 java/1.8.0_242 vendor/Oracle_Corporation cfg/retry-mode/legacy", "requestParameters": {"subscriptionName": "beluRdsEventSubscription", "snsTopicArn": "arn:aws:sns:us-east-1:444000444:test", "sourceType": "db-instance", "sourceIds": ["belu-metadata-database-1-instance-1", "belu-mysql-database-1"]}, "responseElements": {"customerAwsId": "444000444", "custSubscriptionId": "beluRdsEventSubscription", "snsTopicArn": "arn:aws:sns:us-east-1:444000444:test", "status": "active", "subscriptionCreationTime": "Tue Jun 29 12:21:35 UTC 2021", "sourceType": "db-instance", "sourceIdsList": ["belu-metadata-database-1-instance-1", "belu-mysql-database-1"], "enabled": true, "eventSubscriptionArn": "arn:aws:rds:us-east-1:444000444:es:beluRdsEventSubscription"}, "requestID": "b7ef566c-d266-446a-a617-9ddff87cafd7", "eventID": "941338b4-bc46-4b2f-8b7e-9149fcf23bb7", "readOnly": false, "eventType": "AwsApiCall", "managementEvent": true, "eventCategory": "Management", "recipientAccountId": "444000444"}',
            'cloud.provider': 'aws',
            'cloud.account.id': '444000444',
            'cloud.region': 'us-east-1',
            'aws.log_group': 'aws-cloudtrail-logs-444000444-1cceb782',
            'aws.log_stream': '444000444_CloudTrail_us-east-1',
            'aws.region': 'us-east-1',
            'aws.account.id': '444000444',
            'severity': 'INFO',
            'timestamp': 1622554840009,
            'audit.action': 'CreateEventSubscription',
            'audit.identity': 'arn:aws:iam::444000444:user/somemonitoringuser',
            'audit.result': 'Succeeded'}
    }, id="testcase_Cloudtrail_RDS_CreateEventSubscription_multiple_resources_with_source_type"),

    pytest.param({
        "record_data_decoded": {
            "messageType": "DATA_MESSAGE",
            "owner": "444000444",
            "logGroup": "/aws/apprunner/MNA-test-sample/0842920903ba4b86bc4914aebfd1fb71/application",
            "logStream": "instance/ee2c02336dbe4222936bea385d900d0a",
            "subscriptionFilters": ["dt-aws-logs"],
            "logEvents": [{
                "id": "36278401907111421594688977684007571489764321972201324544",
                "timestamp": 1626779804179,
                "message": "INFO:root:Generating avatar image"
            }
            ]
        },
        "expect_first_log_contains": {
            'aws.service': 'apprunner',
            'aws.resource.id': 'MNA-test-sample',
            'aws.arn': 'arn:aws:apprunner:us-east-1:444000444:service/MNA-test-sample/0842920903ba4b86bc4914aebfd1fb71',
            'dt.source_entity': 'CUSTOM_DEVICE-502D948277535551',
            'content': 'INFO:root:Generating avatar image',
            'cloud.provider': 'aws',
            'cloud.account.id': '444000444',
            'cloud.region': 'us-east-1',
            'aws.log_group': '/aws/apprunner/MNA-test-sample/0842920903ba4b86bc4914aebfd1fb71/application',
            'aws.log_stream': 'instance/ee2c02336dbe4222936bea385d900d0a',
            'aws.region': 'us-east-1',
            'aws.account.id': '444000444',
            'severity': 'INFO',
            'timestamp': 1626779804179}
    }, id="testcase_App_Runner_application_logs"),

    pytest.param({
        "record_data_decoded": {
            "messageType": "DATA_MESSAGE",
            "owner": "444000444",
            "logGroup": "/aws/apprunner/MNA-test-sample/0842920903ba4b86bc4914aebfd1fb71/application",
            "logStream": "instance/ee2c02336dbe4222936bea385d900d0a",
            "subscriptionFilters": ["dt-aws-logs"],
            "logEvents": [{
                "id": "36278412331460960176637582018679695718665678823625654272",
                "timestamp": 1626779804180,
                "message": "WARNING: root: danger! danger!"
            }
            ]
        },
        "expect_first_log_contains": {
            'severity': 'WARN'
        }
    }, id="testcase_App_Runner_application_logs_severity_warn"),

    pytest.param({
        "record_data_decoded": {
            "messageType": "DATA_MESSAGE",
            "owner": "444000444",
            "logGroup": "/aws/apprunner/MNA-test-sample/0842920903ba4b86bc4914aebfd1fb71/application",
            "logStream": "instance/ee2c02336dbe4222936bea385d900d0a",
            "subscriptionFilters": ["dt-aws-logs"],
            "logEvents": [{
                "id": "36278412338106582245799707715098908212405235687668776960",
                "timestamp": 1626779804181,
                "message": "ERROR This is fine."
            }
            ]
        },
        "expect_first_log_contains": {
            'severity': 'ERROR'
        }
    }, id="testcase_App_Runner_application_logs_severity_error"),

    pytest.param({
        "record_data_decoded": {
            "messageType": "DATA_MESSAGE",
            "owner": "444000444",
            "logGroup": "/aws/apprunner/MNA-test-sample/0842920903ba4b86bc4914aebfd1fb71/service",
            "logStream": "events",
            "subscriptionFilters": ["dt-aws-logs"],
            "logEvents": [{
                "id": "36278412234742628250610269448515044290183004986164903936",
                "timestamp": 1626780267286,
                "message": "[AppRunner] Service status is set to OPERATION_IN_PROGRESS."
            }
            ]
        },
        "expect_first_log_contains": {
            'aws.service': 'apprunner',
            'aws.resource.id': 'MNA-test-sample',
            'aws.arn': 'arn:aws:apprunner:us-east-1:444000444:service/MNA-test-sample/0842920903ba4b86bc4914aebfd1fb71',
            'dt.source_entity': 'CUSTOM_DEVICE-502D948277535551',
            'content': '[AppRunner] Service status is set to OPERATION_IN_PROGRESS.',
            'cloud.provider': 'aws',
            'cloud.account.id': '444000444',
            'cloud.region': 'us-east-1',
            'aws.log_group': '/aws/apprunner/MNA-test-sample/0842920903ba4b86bc4914aebfd1fb71/service',
            'aws.log_stream': 'events',
            'aws.region': 'us-east-1',
            'aws.account.id': '444000444',
            'severity': 'INFO',
            'timestamp': 1626780267286}
    }, id="testcase_App_Runner_service_logs"),

    pytest.param({
        "record_data_decoded": {
            "messageType": "DATA_MESSAGE",
            "owner": "444000444",
            "logGroup": "sns/us-east-1/444000444/sample-sns-logs-generator",
            "logStream": "b8127c1a-7f79-4e71-bc66-f6573803c831",
            "subscriptionFilters": ["sample-aws-logs"],
            "logEvents": [{
                "id": "36290104942576390643781035518045227821322519144175435776",
                "timestamp": 1627304586439,
                "message": "{\"notification\":{\"messageMD5Sum\":\"d7f9e409f27b6f8e7b70a5f011a00e13\",\"messageId\":\"a37084ce-24f0-5325-a4de-ddb69065354e\",\"topicArn\":\"arn:aws:sns:us-east-1:444000444:sample-sns-logs-generator\",\"timestamp\":\"2021-07-26 13:02:13.706\"},\"delivery\":{\"deliveryId\":\"82f09c7b-c844-5e16-b1a5-c5037cd15fab\",\"destination\":\"arn:aws:sqs:us-east-1:444000444:sample-sns-subscriber\",\"providerResponse\":\"{\\\"sqsRequestId\\\":\\\"236a3aac-74c1-5187-acb7-63d4c054d1e1\\\",\\\"sqsMessageId\\\":\\\"7bebbb93-8399-4747-a9ca-843ce5813315\\\"}\",\"dwellTimeMs\":48,\"attempts\":1,\"statusCode\":200},\"status\":\"SUCCESS\"}"
            }
            ]
        },
        "expect_first_log_contains": {
            'aws.service': 'sns',
            'aws.resource.id': 'sample-sns-logs-generator',
            'aws.arn': 'arn:aws:sns:us-east-1:444000444:sample-sns-logs-generator',
            'dt.source_entity': 'CUSTOM_DEVICE-F2FBC0402737EF69',
            'content': '{\"notification\":{\"messageMD5Sum\":\"d7f9e409f27b6f8e7b70a5f011a00e13\",\"messageId\":\"a37084ce-24f0-5325-a4de-ddb69065354e\",\"topicArn\":\"arn:aws:sns:us-east-1:444000444:sample-sns-logs-generator\",\"timestamp\":\"2021-07-26 13:02:13.706\"},\"delivery\":{\"deliveryId\":\"82f09c7b-c844-5e16-b1a5-c5037cd15fab\",\"destination\":\"arn:aws:sqs:us-east-1:444000444:sample-sns-subscriber\",\"providerResponse\":\"{\\\"sqsRequestId\\\":\\\"236a3aac-74c1-5187-acb7-63d4c054d1e1\\\",\\\"sqsMessageId\\\":\\\"7bebbb93-8399-4747-a9ca-843ce5813315\\\"}\",\"dwellTimeMs\":48,\"attempts\":1,\"statusCode\":200},\"status\":\"SUCCESS\"}',
            'cloud.provider': 'aws',
            'cloud.account.id': '444000444',
            'cloud.region': 'us-east-1',
            'aws.log_group': 'sns/us-east-1/444000444/sample-sns-logs-generator',
            'aws.log_stream': 'b8127c1a-7f79-4e71-bc66-f6573803c831',
            'aws.region': 'us-east-1',
            'aws.account.id': '444000444',
            'severity': 'INFO',
            'timestamp': 1627304586439}
    }, id="testcase_SNS_success"),

    pytest.param({
        "record_data_decoded": {
            "messageType": "DATA_MESSAGE",
            "owner": "444000444",
            "logGroup": "sns/us-east-1/444000444/sample-sns-logs-generator_123.fifo/Failure",
            "logStream": "297f5c53-6372-40d5-8129-7a75174a85e2",
            "subscriptionFilters": ["sample-aws-logs"],
            "logEvents": [{
                "id": "36290210055711636225167258963783667929263292187971747840",
                "timestamp": 1627309299875,
                "message": "{\"notification\":{\"messageMD5Sum\":\"4fbd6baa3908ceecb6d3a49314bc1d71\",\"messageId\":\"71db8efc-3022-50d3-8b55-d784f706e076\",\"topicArn\":\"arn:aws:sns:us-east-1:444000444:sample-sns-logs-generator\",\"timestamp\":\"2021-07-26 14:21:24.892\"},\"delivery\":{\"deliveryId\":\"587300b1-c463-5014-a540-59c903479503\",\"destination\":\"arn:aws:sqs:us-east-1:444000444:sample-sns-subscriber-2\",\"providerResponse\":\"{\\\"ErrorCode\\\":\\\"AccessDenied\\\",\\\"ErrorMessage\\\":\\\"Access to the resource https://sqs.us-east-1.amazonaws.com/444000444/sample-sns-subscriber-2 is denied.\\\",\\\"sqsRequestId\\\":\\\"Unrecoverable\\\"}\",\"dwellTimeMs\":37,\"attempts\":1,\"statusCode\":403},\"status\":\"FAILURE\"}"
            }
            ]
        },
        "expect_first_log_contains": {
            'aws.service': 'sns',
            'aws.resource.id': 'sample-sns-logs-generator_123.fifo',
            'aws.arn': 'arn:aws:sns:us-east-1:444000444:sample-sns-logs-generator_123.fifo',
            'dt.source_entity': 'CUSTOM_DEVICE-C68F57C6DC1F68C1',
            'content': '{\"notification\":{\"messageMD5Sum\":\"4fbd6baa3908ceecb6d3a49314bc1d71\",\"messageId\":\"71db8efc-3022-50d3-8b55-d784f706e076\",\"topicArn\":\"arn:aws:sns:us-east-1:444000444:sample-sns-logs-generator\",\"timestamp\":\"2021-07-26 14:21:24.892\"},\"delivery\":{\"deliveryId\":\"587300b1-c463-5014-a540-59c903479503\",\"destination\":\"arn:aws:sqs:us-east-1:444000444:sample-sns-subscriber-2\",\"providerResponse\":\"{\\\"ErrorCode\\\":\\\"AccessDenied\\\",\\\"ErrorMessage\\\":\\\"Access to the resource https://sqs.us-east-1.amazonaws.com/444000444/sample-sns-subscriber-2 is denied.\\\",\\\"sqsRequestId\\\":\\\"Unrecoverable\\\"}\",\"dwellTimeMs\":37,\"attempts\":1,\"statusCode\":403},\"status\":\"FAILURE\"}',
            'cloud.provider': 'aws',
            'cloud.account.id': '444000444',
            'cloud.region': 'us-east-1',
            'aws.log_group': 'sns/us-east-1/444000444/sample-sns-logs-generator_123.fifo/Failure',
            'aws.log_stream': '297f5c53-6372-40d5-8129-7a75174a85e2',
            'aws.region': 'us-east-1',
            'aws.account.id': '444000444',
            'severity': 'ERROR',
            'timestamp': 1627309299875}
    }, id="testcase_SNS_failure"),

    pytest.param({
        "record_data_decoded": {
            "logGroup": "/aws/rds/instance/mysql-db-for-logs/audit",
            "logStream": "mysql-db-for-logs",
            "messageType": "DATA_MESSAGE",
            "owner": "444000444",
            "subscriptionFilters": ["mysql-audit-filter"],
            "logEvents": [
                {
                    "id": "35958590510527767165636549608812769529777864588249006080",
                    "timestamp": "12345",
                    "message": "20210722 17:15:28,ip-10-1-3-230,admin,157.25.19.100,13,0,DISCONNECT,testdb,,0,SSL"
                }
            ],
        },
        "expect_first_log_contains": {
            "aws.service": "rds",
            "aws.resource.id": "mysql-db-for-logs",
            "aws.arn": "arn:aws:rds:us-east-1:444000444:db:mysql-db-for-logs",
            "dt.source_entity": "RELATIONAL_DATABASE_SERVICE-055A2525EFDA9A63",
            'content': "20210722 17:15:28,ip-10-1-3-230,admin,157.25.19.100,13,0,DISCONNECT,testdb,,0,SSL",
            'cloud.provider': 'aws',
            'cloud.account.id': "444000444",
            'cloud.region': "us-east-1",
            'aws.log_group': "/aws/rds/instance/mysql-db-for-logs/audit",
            'aws.log_stream': "mysql-db-for-logs",
            'aws.region': "us-east-1",
            'aws.account.id': "444000444",
            'severity': 'INFO',
            'log.source': 'rds - audit logs',
        }
    }, id="testcase_rds_mysql_audit_log"),

    pytest.param({
        "record_data_decoded": {
            "logGroup": "/aws/rds/instance/mysql-db-for-logs/slowquery",
            "logStream": "mysql-db-for-logs",
            "messageType": "DATA_MESSAGE",
            "owner": "444000444",
            "subscriptionFilters": ["mysql-audit-filter"],
            "logEvents": [
                {
                    "id": "35958590510527767165636549608812769529777864588249006080",
                    "timestamp": "12345",
                    "message": "# Time: 2021-07-22T17:11:45.948278Z \nUser@Host: rdsadmin[rdsadmin] @ localhost [127.0.0.1]  Id:     7\nQuery_time: 0.000964  Lock_time: 0.000000 Rows_sent: 1  Rows_examined: 1\nSET timestamp=1626973905;\nSELECT @@GLOBAL.read_only;"
                }
            ],
        },
        "expect_first_log_contains": {
            "aws.service": "rds",
            "aws.resource.id": "mysql-db-for-logs",
            "aws.arn": "arn:aws:rds:us-east-1:444000444:db:mysql-db-for-logs",
            "dt.source_entity": "RELATIONAL_DATABASE_SERVICE-055A2525EFDA9A63",
            'content': "# Time: 2021-07-22T17:11:45.948278Z \nUser@Host: rdsadmin[rdsadmin] @ localhost [127.0.0.1]  Id:     7\nQuery_time: 0.000964  Lock_time: 0.000000 Rows_sent: 1  Rows_examined: 1\nSET timestamp=1626973905;\nSELECT @@GLOBAL.read_only;",
            'cloud.provider': 'aws',
            'cloud.account.id': "444000444",
            'cloud.region': "us-east-1",
            'aws.log_group': "/aws/rds/instance/mysql-db-for-logs/slowquery",
            'aws.log_stream': "mysql-db-for-logs",
            'aws.region': "us-east-1",
            'aws.account.id': "444000444",
            'severity': 'WARNING',
            'log.source': 'rds - slowquery logs',
        }
    }, id="testcase_rds_mysql_slowquery_log"),

    pytest.param({
        "record_data_decoded": {
            "logGroup": "/aws/rds/instance/mysql-db-for-logs/audit",
            "logStream": "mysql-db-for-logs",
            "messageType": "DATA_MESSAGE",
            "owner": "444000444",
            "subscriptionFilters": ["mysql-audit-filter"],
            "logEvents": [
                {
                    "id": "35958590510527767165636549608812769529777864588249006080",
                    "timestamp": "12345",
                    "message": "20210722 17:15:28,ip-10-1-3-230,admin,157.25.19.100,13,0,DISCONNECT,testdb,,0,SSL"
                }
            ],
        },
        "expect_first_log_contains": {
            "aws.service": "rds",
            "aws.resource.id": "mysql-db-for-logs",
            "aws.arn": "arn:aws:rds:us-east-1:444000444:db:mysql-db-for-logs",
            "dt.source_entity": "RELATIONAL_DATABASE_SERVICE-055A2525EFDA9A63",
            'content': "20210722 17:15:28,ip-10-1-3-230,admin,157.25.19.100,13,0,DISCONNECT,testdb,,0,SSL",
            'cloud.provider': 'aws',
            'cloud.account.id': "444000444",
            'cloud.region': "us-east-1",
            'aws.log_group': "/aws/rds/instance/mysql-db-for-logs/audit",
            'aws.log_stream': "mysql-db-for-logs",
            'aws.region': "us-east-1",
            'aws.account.id': "444000444",
            'severity': 'INFO',
            'log.source': 'rds - audit logs',
        }
    }, id="testcase_rds_mysql_audit_log"),

    pytest.param({
        "record_data_decoded": {
            "logGroup": "/aws/rds/instance/mysql-db-for-logs/slowquery",
            "logStream": "mysql-db-for-logs",
            "messageType": "DATA_MESSAGE",
            "owner": "444000444",
            "subscriptionFilters": ["mysql-audit-filter"],
            "logEvents": [
                {
                    "id": "35958590510527767165636549608812769529777864588249006080",
                    "timestamp": "12345",
                    "message": "# Time: 2021-07-22T17:11:45.948278Z \nUser@Host: rdsadmin[rdsadmin] @ localhost [127.0.0.1]  Id:     7\nQuery_time: 0.000964  Lock_time: 0.000000 Rows_sent: 1  Rows_examined: 1\nSET timestamp=1626973905;\nSELECT @@GLOBAL.read_only;"
                }
            ],
        },
        "expect_first_log_contains": {
            "aws.service": "rds",
            "aws.resource.id": "mysql-db-for-logs",
            "aws.arn": "arn:aws:rds:us-east-1:444000444:db:mysql-db-for-logs",
            "dt.source_entity": "RELATIONAL_DATABASE_SERVICE-055A2525EFDA9A63",
            'content': "# Time: 2021-07-22T17:11:45.948278Z \nUser@Host: rdsadmin[rdsadmin] @ localhost [127.0.0.1]  Id:     7\nQuery_time: 0.000964  Lock_time: 0.000000 Rows_sent: 1  Rows_examined: 1\nSET timestamp=1626973905;\nSELECT @@GLOBAL.read_only;",
            'cloud.provider': 'aws',
            'cloud.account.id': "444000444",
            'cloud.region': "us-east-1",
            'aws.log_group': "/aws/rds/instance/mysql-db-for-logs/slowquery",
            'aws.log_stream': "mysql-db-for-logs",
            'aws.region': "us-east-1",
            'aws.account.id': "444000444",
            'severity': 'WARNING',
            'log.source': 'rds - slowquery logs',
        }
    }, id="testcase_rds_mysql_slowquery_log"),

    pytest.param({
        "record_data_decoded": {
            "logGroup": "/aws/rds/cluster/aurora-mysql/general",
            "logStream": "aurora-mysql-instance-1",
            "messageType": "DATA_MESSAGE",
            "owner": "444000444",
            "subscriptionFilters": ["mysql-audit-filter"],
            "logEvents": [
                {
                    "id": "35958590510527767165636549608812769529777864588249006080",
                    "timestamp": "12345",
                    "message": "2021-08-10T09:57:26.077268Z    2 Query	SELECT durable_lsn, current_read_point, server_id, last_update_timestamp FROM information_schema.replica_host_status;"
                }
            ],
        },
        "expect_first_log_contains": {
            "aws.service": "rds",
            "aws.resource.id": "aurora-mysql",
            "aws.arn": "arn:aws:rds:us-east-1:444000444:db:aurora-mysql-instance-1",
            "dt.source_entity": "RELATIONAL_DATABASE_SERVICE-FC361C8F808383AE",
            'content': "2021-08-10T09:57:26.077268Z    2 Query	SELECT durable_lsn, current_read_point, server_id, last_update_timestamp FROM information_schema.replica_host_status;",
            'cloud.provider': 'aws',
            'cloud.account.id': "444000444",
            'cloud.region': "us-east-1",
            'aws.log_group': "/aws/rds/cluster/aurora-mysql/general",
            'aws.log_stream': "aurora-mysql-instance-1",
            'aws.region': "us-east-1",
            'aws.account.id': "444000444",
            'severity': 'INFO',
            'log.source': 'rds - general logs',
        },
        "perf_check": {
            "repeat_record": 10000,
            "time_limit_sec": 5
            # roughly 1,5MB of content, ~7MB counting whole log entry with metadata
        }
    }, id="testcase_rds_aurora_mysql_general_log"),

    pytest.param({
        "record_data_decoded": {
            "logGroup": "/aws/rds/cluster/aurora-mysql/slowquery",
            "logStream": "aurora-mysql-instance-1",
            "messageType": "DATA_MESSAGE",
            "owner": "444000444",
            "subscriptionFilters": ["mysql-audit-filter"],
            "logEvents": [
                {
                    "id": "35958590510527767165636549608812769529777864588249006080",
                    "timestamp": "12345",
                    "message": "# Time: 2021-08-10T11:28:20.581705Z\n# User@Host: rdsadmin[rdsadmin] @ localhost []  Id:     3\n# Query_time: 0.000216  Lock_time: 0.000000 Rows_sent: 0  Rows_examined: 0\nSET timestamp=1628594900;\nCOMMIT;"
                }
            ],
        },
        "expect_first_log_contains": {
            "aws.service": "rds",
            "aws.resource.id": "aurora-mysql",
            "aws.arn": "arn:aws:rds:us-east-1:444000444:db:aurora-mysql-instance-1",
            "dt.source_entity": "RELATIONAL_DATABASE_SERVICE-FC361C8F808383AE",
            'content': "# Time: 2021-08-10T11:28:20.581705Z\n# User@Host: rdsadmin[rdsadmin] @ localhost []  Id:     3\n# Query_time: 0.000216  Lock_time: 0.000000 Rows_sent: 0  Rows_examined: 0\nSET timestamp=1628594900;\nCOMMIT;",
            'cloud.provider': 'aws',
            'cloud.account.id': "444000444",
            'cloud.region': "us-east-1",
            'aws.log_group': "/aws/rds/cluster/aurora-mysql/slowquery",
            'aws.log_stream': "aurora-mysql-instance-1",
            'aws.region': "us-east-1",
            'aws.account.id': "444000444",
            'severity': 'WARNING',
            'log.source': 'rds - slowquery logs',
        }
    }, id="testcase_rds_aurora_mysql_slowquery_log"),

    pytest.param({
        "record_data_decoded": {
            "logGroup": "/aws/rds/cluster/aurora-mysql/error",
            "logStream": "aurora-mysql-instance-1",
            "messageType": "DATA_MESSAGE",
            "owner": "444000444",
            "subscriptionFilters": ["mysql-audit-filter"],
            "logEvents": [
                {
                    "id": "35958590510527767165636549608812769529777864588249006080",
                    "timestamp": "12345",
                    "message": "2021-08-10T09:20:23.582919Z 0 [Warning] InnoDB: Setting innodb_checksums to OFF is DEPRECATED. This option may be removed in future releases. You should set innodb_checksum_algorithm=NONE instead."
                }
            ],
        },
        "expect_first_log_contains": {
            "aws.service": "rds",
            "aws.resource.id": "aurora-mysql",
            "aws.arn": "arn:aws:rds:us-east-1:444000444:db:aurora-mysql-instance-1",
            "dt.source_entity": "RELATIONAL_DATABASE_SERVICE-FC361C8F808383AE",
            'content': "2021-08-10T09:20:23.582919Z 0 [Warning] InnoDB: Setting innodb_checksums to OFF is DEPRECATED. This option may be removed in future releases. You should set innodb_checksum_algorithm=NONE instead.",
            'cloud.provider': 'aws',
            'cloud.account.id': "444000444",
            'cloud.region': "us-east-1",
            'aws.log_group': "/aws/rds/cluster/aurora-mysql/error",
            'aws.log_stream': "aurora-mysql-instance-1",
            'aws.region': "us-east-1",
            'aws.account.id': "444000444",
            'severity': 'WARNING',
            'log.source': 'rds - error logs',
        }
    }, id="testcase_rds_aurora_mysql_error_log"),

    pytest.param({
        "record_data_decoded": {
            "logGroup": "/aws/rds/cluster/aurora-mysql/error",
            "logStream": "aurora-mysql-instance-1",
            "messageType": "DATA_MESSAGE",
            "owner": "444000444",
            "subscriptionFilters": ["mysql-audit-filter"],
            "logEvents": [
                {
                    "id": "35958590510527767165636549608812769529777864588249006080",
                    "timestamp": "12345",
                    "message": "2021-08-10T09:20:26.366088Z 0 [Note] /rdsdbbin/oscar/bin/mysqld: ready for connections.\nVersion: '5.7.12-log'  socket: '/tmp/mysql.sock'  port: 3306  MySQL Community Server (GPL)\n  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current\n                                 Dload  Upload   Total   Spent    Left  Speed\n\n  0     0    0     0    0     0      0      0 --:--:-- --:--:-- --:--:--     0\n100     8  100     8    0     0   8000      0 --:--:-- --:--:-- --:--:--  8000\n"
                }
            ],
        },
        "expect_first_log_contains": {
            "aws.service": "rds",
            "aws.resource.id": "aurora-mysql",
            "aws.arn": "arn:aws:rds:us-east-1:444000444:db:aurora-mysql-instance-1",
            "dt.source_entity": "RELATIONAL_DATABASE_SERVICE-FC361C8F808383AE",
            'content': "2021-08-10T09:20:26.366088Z 0 [Note] /rdsdbbin/oscar/bin/mysqld: ready for connections.\nVersion: '5.7.12-log'  socket: '/tmp/mysql.sock'  port: 3306  MySQL Community Server (GPL)\n  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current\n                                 Dload  Upload   Total   Spent    Left  Speed\n\n  0     0    0     0    0     0      0      0 --:--:-- --:--:-- --:--:--     0\n100     8  100     8    0     0   8000      0 --:--:-- --:--:-- --:--:--  8000\n",
            'cloud.provider': 'aws',
            'cloud.account.id': "444000444",
            'cloud.region': "us-east-1",
            'aws.log_group': "/aws/rds/cluster/aurora-mysql/error",
            'aws.log_stream': "aurora-mysql-instance-1",
            'aws.region': "us-east-1",
            'aws.account.id': "444000444",
            'severity': 'INFO',
            'log.source': 'rds - error logs',
        }
    }, id="testcase_rds_aurora_mysql_error_log"),

    pytest.param({
        "record_data_decoded": {
            "logGroup": "/aws/rds/cluster/aurora-postresql/postgresql",
            "logStream": "aurora-postresql-instance-1.0",
            "messageType": "DATA_MESSAGE",
            "owner": "444000444",
            "subscriptionFilters": ["mysql-audit-filter"],
            "logEvents": [
                {
                    "id": "35958590510527767165636549608812769529777864588249006080",
                    "timestamp": "12345",
                    "message": "2021-08-10 09:20:53 UTC::@:[7701]:LOG:  skipping missing configuration file \"/rdsdbdata/db/postgresql.auto.conf\""
                }
            ],
        },
        "expect_first_log_contains": {
            "aws.service": "rds",
            "aws.resource.id": "aurora-postresql",
            "aws.arn": "arn:aws:rds:us-east-1:444000444:db:aurora-postresql-instance-1",
            "dt.source_entity": "RELATIONAL_DATABASE_SERVICE-952B74DD9DB9E3DE",
            'content': "2021-08-10 09:20:53 UTC::@:[7701]:LOG:  skipping missing configuration file \"/rdsdbdata/db/postgresql.auto.conf\"",
            'cloud.provider': 'aws',
            'cloud.account.id': "444000444",
            'cloud.region': "us-east-1",
            'aws.log_group': "/aws/rds/cluster/aurora-postresql/postgresql",
            'aws.log_stream': "aurora-postresql-instance-1.0",
            'aws.region': "us-east-1",
            'aws.account.id': "444000444",
            'severity': 'INFO',
            'log.source': 'rds - postgresql logs',
        }
    }, id="testcase_rds_aurora_postgresql_log"),

    pytest.param({
        "record_data_decoded": {
            "logGroup": "/aws/rds/cluster/aurora-postresql/postgresql",
            "logStream": "aurora-postresql-instance-1.0",
            "messageType": "DATA_MESSAGE",
            "owner": "444000444",
            "subscriptionFilters": ["mysql-audit-filter"],
            "logEvents": [
                {
                    "id": "35958590510527767165636549608812769529777864588249006080",
                    "timestamp": "12345",
                    "message": "2021-08-10 09:20:53 UTC::@:[7701]:WARNING:  skipping missing configuration file \"/rdsdbdata/db/postgresql.auto.conf\""
                }
            ],
        },
        "expect_first_log_contains": {
            "aws.service": "rds",
            "aws.resource.id": "aurora-postresql",
            "aws.arn": "arn:aws:rds:us-east-1:444000444:db:aurora-postresql-instance-1",
            "dt.source_entity": "RELATIONAL_DATABASE_SERVICE-952B74DD9DB9E3DE",
            'content': "2021-08-10 09:20:53 UTC::@:[7701]:WARNING:  skipping missing configuration file \"/rdsdbdata/db/postgresql.auto.conf\"",
            'cloud.provider': 'aws',
            'cloud.account.id': "444000444",
            'cloud.region': "us-east-1",
            'aws.log_group': "/aws/rds/cluster/aurora-postresql/postgresql",
            'aws.log_stream': "aurora-postresql-instance-1.0",
            'aws.region': "us-east-1",
            'aws.account.id': "444000444",
            'severity': 'WARNING',
            'log.source': 'rds - postgresql logs',
        }
    }, id="testcase_rds_aurora_postgresql_log"),

])
def test_full_transformation(testcase: dict):
    context = Context("function-name", "dt-url", "dt-token", False, False)

    record_data_decoded = testcase["record_data_decoded"]
    expect_first_log_contains = testcase["expect_first_log_contains"]

    logs_sent = []

    if "perf_check" in testcase:
        perf_check = testcase["perf_check"]
        repeat_record = perf_check["repeat_record"]
        time_limit_sec = perf_check["time_limit_sec"]

        start_sec = time.time()
        for i in range(repeat_record):
            logs_sent = logs.transformation.extract_dt_logs_from_single_record(
                json.dumps(record_data_decoded), BATCH_METADATA, context)
        end_sec = time.time()
        duration_sec = end_sec - start_sec
        print(f"PERF_CHECK {duration_sec}")
        assert duration_sec < time_limit_sec, f"Perf check: duration ({duration_sec}) should be less than limit {time_limit_sec}"
    else:
        logs_sent = logs.transformation.extract_dt_logs_from_single_record(
            json.dumps(record_data_decoded), BATCH_METADATA, context)

    assert len(logs_sent) == len(record_data_decoded["logEvents"])

    first_log = logs_sent[0]

    for k, expected_value in expect_first_log_contains.items():
        if expected_value == None:
            assert k not in first_log, f"key={k} not expected in the output, actual={first_log[k]}"
        else:
            assert first_log.get(k,
                                 None) == expected_value, f"key={k}, expected value={expected_value}, actual={first_log.get(k, None)}"
