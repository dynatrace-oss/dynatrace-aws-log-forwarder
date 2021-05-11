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

BATCH_METADATA = BatchMetadata("444000444", "us-east-1", "aws")


@pytest.mark.parametrize("testcase", [

    ({
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
    }),

    ({
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
            "dt.source_entity_type": "AWS_LAMBDA_FUNCTION",
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
    }),

])
def test_full_transformation(testcase: dict):
    record_data_decoded = testcase["record_data_decoded"]
    expect_first_log_contains = testcase["expect_first_log_contains"]

    logs_sent = logs.transformation.extract_dt_logs_from_single_record(json.dumps(record_data_decoded), BATCH_METADATA)

    assert len(logs_sent) == len(record_data_decoded["logEvents"])

    first_log = logs_sent[0]

    for k, v in expect_first_log_contains.items():
        assert k in first_log
        assert first_log[k] == v
