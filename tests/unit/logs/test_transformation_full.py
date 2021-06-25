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

import pytest

import logs.main
import logs.transformation
from logs.models.batch_metadata import BatchMetadata
from util.context import Context

BATCH_METADATA = BatchMetadata("444000444", "us-east-1", "aws")


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
                               +"Traceback (most recent call last):\n"
                               +"  File \"/var/task/lambda_function.py\", line 101, in lambda_handler\n"
                               +"    print(i.__str__() + single_log_entry)"
                }
            ],
        },
        "expect_first_log_contains": {
            "aws.service": "lambda",
            "aws.resource.id": "dynatrace-aws-logs-Lambda-1K7HG2Q2LIQKU",
            "aws.arn": "arn:aws:lambda:us-east-1:444000444:function:dynatrace-aws-logs-Lambda-1K7HG2Q2LIQKU",
            "dt.source_entity": "AWS_LAMBDA_FUNCTION-F141CAEAE2BED565",
            'content': "[ERROR] UnboundLocalError: local variable 'single_log_entry' referenced before assignment\n"
                       +"Traceback (most recent call last):\n"
                       +"  File \"/var/task/lambda_function.py\", line 101, in lambda_handler\n"
                       +"    print(i.__str__() + single_log_entry)",
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
                                                   "userIdentity": {
                                                       "type": "IAMUser",
                                                       "principalId": "AIDA12345667789ABCEF",
                                                       "arn": "arn:aws:iam::444000444:user/somemonitoringuser",
                                                       "accountId": "444000444",
                                                       "accessKeyId": "AKIA123456789ABCDEFG",
                                                       "userName": "Dynatrace_monitoring_user"
                                                   },
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
                                               },
                                              {"id": "36184182057683330175263108764349521965726085205046394889",
                                               "timestamp": 1622554840009,
                                               "message": "{\"eventVersion\":\"1.08\",\"userIdentity\":{\"type\":\"IAMUser\",\"principalId\":\"AIDA5G26WOZYV56B23PDL\",\"arn\":\"arn:aws:iam::444000444:user/Dynatrace_monitoring_user\",\"accountId\":\"444000444\",\"accessKeyId\":\"AIDA12345667789ABCEF\",\"userName\":\"Dynatrace_monitoring_user\"},\"eventTime\":\"2021-06-01T13:29:17Z\",\"eventSource\":\"rds.amazonaws.com\",\"eventName\":\"DescribeDBInstances\",\"awsRegion\":\"eu-north-1\",\"sourceIPAddress\":\"157.25.19.100\",\"userAgent\":\"aws-sdk-java/1.11.789 Linux/5.4.0-56-generic OpenJDK_64-Bit_Server_VM/11.0.8+10 java/11.0.8 vendor/AdoptOpenJDK\",\"requestParameters\":null,\"responseElements\":null,\"requestID\":\"0a58cb63-bb56-4e63-9883-98bf0ae258ed\",\"eventID\":\"5e83e0d1-c17a-4bbd-980a-7221cacbacdc\",\"readOnly\":true,\"eventType\":\"AwsApiCall\",\"managementEvent\":true,\"eventCategory\":\"Management\",\"recipientAccountId\":\"444000444\"}" }
                                              ]},
        "expect_first_log_contains": {
            'aws.service': 'cloudtrail',
            # "aws.resource.id": "TODO",
            # "aws.arn": "arn:aws:TODO:us-east-1::/restapis/8zcb3dxf4l",
            'content': '{"eventVersion": "1.08", "userIdentity": {"type": "IAMUser", "principalId": "AIDA12345667789ABCEF", "arn": "arn:aws:iam::444000444:user/somemonitoringuser", "accountId": "444000444", "accessKeyId": "AKIA123456789ABCDEFG", "userName": "Dynatrace_monitoring_user"}, "eventTime": "2021-05-28T11:39:33Z", "eventSource": "rds.amazonaws.com", "eventName": "DescribeEvents", "awsRegion": "ap-southeast-2", "sourceIPAddress": "155.55.55.055", "userAgent": "aws-sdk-java/1.11.789 Linux/5.4.0-56-generic OpenJDK_64-Bit_Server_VM/11.0.8+10 java/11.0.8 vendor/AdoptOpenJDK", "requestParameters": {"startTime": "May 28, 2021 11:29:00 AM", "endTime": "May 28, 2021 11:34:00 AM"}, "responseElements": null, "requestID": "69de2278-ef7a-4b9a-bdc5-a78c9210ea4e", "eventID": "249491df-4970-421d-8575-5bf555357c14", "readOnly": true, "eventType": "AwsApiCall", "managementEvent": true, "eventCategory": "Management", "recipientAccountId": "444000444"}',
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
    }, id="testcase_Cloudtrail_RDS"),

    pytest.param({
        "record_data_decoded": {"messageType": "DATA_MESSAGE", "owner": "444000444",
                                "logGroup": "aws-cloudtrail-logs-444000444-1cceb782",
                                "logStream": "444000444_CloudTrail_us-east-1",
                                "subscriptionFilters": ["Belu-APM-299389-cloudtrail-RDS_subscriptionFilter"],
                                "logEvents": [{"id": "36184182057683330175263108764349521965726085205046394887",
                                               "timestamp": 1622554840009,
                                               "message": json.dumps({
                                                   "eventVersion": "1.08",
                                                   "userIdentity": {
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
                                                   },
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
            # "aws.resource.id": "TODO",
            # "aws.arn": "arn:aws:TODO:us-east-1::/restapis/8zcb3dxf4l",
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
    }, id="testcase_Cloudtrail_RDS_error"),

])
def test_full_transformation(testcase: dict):
    context = Context("function-name", "dt-url", "dt-token", False, False)

    record_data_decoded = testcase["record_data_decoded"]
    expect_first_log_contains = testcase["expect_first_log_contains"]

    logs_sent = logs.transformation.extract_dt_logs_from_single_record(
        json.dumps(record_data_decoded), BATCH_METADATA, context)

    assert len(logs_sent) == len(record_data_decoded["logEvents"])

    first_log = logs_sent[0]

    for k, v in expect_first_log_contains.items():
        assert k in first_log
        assert first_log[k] == v, "key={key}, expected value={expected}, actual={actual}".format(key=k, expected=v, actual=first_log[k])
