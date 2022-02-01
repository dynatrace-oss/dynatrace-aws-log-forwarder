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
from dataclasses import dataclass
from typing import List, Dict

from logs.metadata_engine.metadata_engine import MetadataEngine
from logs.models.batch_metadata import BatchMetadata
from util.context import Context

metadata_engine = MetadataEngine()


@dataclass
class RecordMetadata:
    log_group: str
    log_stream: str


def extract_dt_logs_from_single_record(
    record_data_decoded: str, batch_metadata: BatchMetadata, context: Context) -> List[Dict]:
    logs: List[Dict] = []
    record = json.loads(record_data_decoded)

    if record.get('messageType') == 'CONTROL_MESSAGE':
        return []

    record_metadata = RecordMetadata(record["logGroup"], record["logStream"])

    for log_event in record["logEvents"]:
        log_entry = transform_single_log_entry(log_event, batch_metadata, record_metadata, context)
        logs.append(log_entry)

    return logs


def transform_single_log_entry(log_event, batch_metadata, record_metadata, context: Context) -> Dict:
    parsed_record = {
        'content': log_event["message"],
        'cloud.provider': 'aws',
        'cloud.account.id': batch_metadata.account_id,
        'cloud.region': batch_metadata.region,
        'aws.log_group': record_metadata.log_group,
        'aws.log_stream': record_metadata.log_stream,
        'aws.region': batch_metadata.region,
        'aws.account.id': batch_metadata.account_id,
        'severity': 'INFO',
        'cloud.log_forwarder': context.cloud_log_forwarder
    }

    if "timestamp" in log_event:
        parsed_record["timestamp"] = log_event["timestamp"]

    record = {
        'log_stream': record_metadata.log_stream,
        'log_group': record_metadata.log_group,
        'region': batch_metadata.region,
        'partition': batch_metadata.partition,
        'account_id': batch_metadata.account_id,
    }

    # record here is different than Kinesis request record
    # here it is single log entry, in Kinesis request it is a bunch of logs from one logStream

    # record is input for metadata engine (you can use values from record in json configs)
    # parsed_record is output (engine will add generated attributes there)
    metadata_engine.apply(record, parsed_record)

    return parsed_record
