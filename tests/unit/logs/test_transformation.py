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
from unittest.mock import patch

import logs.main
import logs.transformation
from logs.metadata_engine.metadata_engine import MetadataEngine
from logs.models.batch_metadata import BatchMetadata
from util.context import Context

BATCH_METADATA = BatchMetadata("444000444", "us-east-1", "aws")


def get_context(log_forwarder_setup="log.forwarder"):
    return Context("function-name", "dt-url", "dt-token", False, False, log_forwarder_setup, 8192)


@patch.object(MetadataEngine, 'apply')
def test_metadata_engine_input(metadata_engine_apply_mock):
    input_entry = json.dumps({
        "messageType": "DATA_MESSAGE",
        "owner": "444652832050",
        "logGroup": "API-Gateway-Execution-Logs",
        "logStream": "2021-02-04-logstream",
        "subscriptionFilters": ["b-SubscriptionFilter0-1I0DE5MAAFV5G"],
        "logEvents": [
            {
                "id": "35958590510527767165636549608812769529777864588249006080",
                "timestamp": "12345",
                "message": "My log entry",
            },
            {
                "id": "35958590510527767165636549608812769529777864588249006080",
                "message": "My log entry2"
            },
        ],
    })

    actual_output = logs.transformation.extract_dt_logs_from_single_record(
        input_entry, BATCH_METADATA, get_context())

    assert metadata_engine_apply_mock.call_count == 2

    first_call_to_metadata_engine = metadata_engine_apply_mock.call_args_list[0]
    metadata_engine_input = first_call_to_metadata_engine.args[0]

    assert metadata_engine_input == {
        "log_stream": "2021-02-04-logstream",
        "log_group": "API-Gateway-Execution-Logs",
        "region": "us-east-1",
        "partition": "aws",
        "account_id": "444000444",
    }


def test_control_message():
    control_record = json.dumps({
        "messageType": "CONTROL_MESSAGE",
        "owner": "CloudwatchLogs",
        "logGroup": "",
        "logStream": "",
        "subscriptionFilters": [],
        "logEvents": [
            {
                "id": "",
                "timestamp": "1619427317539",
                "message": "CWL CONTROL MESSAGE: Checking health of destination Firehose.",
            },
        ],
    })

    parsed_logs = logs.transformation.extract_dt_logs_from_single_record(
        control_record, BATCH_METADATA, get_context())

    assert len(parsed_logs) == 0


def test_log_forwarder_setup():
    # given
    test_record = json.dumps({
        "messageType": "DATA_MESSAGE",
        "owner": "444652832050",
        "logGroup": "API-Gateway-Execution-Logs",
        "logStream": "2021-02-04-logstream",
        "subscriptionFilters": ["b-SubscriptionFilter0-1I0DE5MAAFV5G"],
        "logEvents": [
            {
                "id": "35958590510527767165636549608812769529777864588249006080",
                "timestamp": "12345",
                "message": "Test message",
            }
        ]
    })

    # when
    forwarder_setup = "MyLogForwarderSetup"
    actual_output = logs.transformation.extract_dt_logs_from_single_record(
        test_record, BATCH_METADATA, get_context(forwarder_setup))

    # then
    assert actual_output[0]['cloud.log_forwarder'] == forwarder_setup
