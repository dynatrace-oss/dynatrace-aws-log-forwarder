import json
from unittest.mock import patch

import logs.main
import logs.transformation
from logs.metadata_engine.metadata_engine import MetadataEngine
from logs.models.batch_metadata import BatchMetadata


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

    batch_metadata = BatchMetadata("444000444", "us-east-1", "aws")
    actual_output = logs.transformation.extract_dt_logs_from_single_record(input_entry, batch_metadata)

    assert metadata_engine_apply_mock.call_count == 2

    first_call_to_metadata_engine = metadata_engine_apply_mock.call_args_list[0]
    metadata_engine_input = first_call_to_metadata_engine.args[0]

    assert metadata_engine_input == {
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

    batch_metadata = BatchMetadata("444000444", "us-east-1", "aws")
    parsed_logs = logs.transformation.extract_dt_logs_from_single_record(control_record, batch_metadata)

    assert len(parsed_logs) == 0
