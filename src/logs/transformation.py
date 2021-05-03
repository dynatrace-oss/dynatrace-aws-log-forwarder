import json
from dataclasses import dataclass
from typing import List, Dict

from logs.metadata_engine.metadata_engine import MetadataEngine
from logs.models.batch_metadata import BatchMetadata

metadata_engine = MetadataEngine()


@dataclass
class RecordMetadata:
    log_group: str
    log_stream: str


def extract_dt_logs_from_single_record(record_data_decoded: str, batch_metadata: BatchMetadata) -> List[Dict]:
    record = json.loads(record_data_decoded)

    if record.get('messageType') == 'CONTROL_MESSAGE':
        return []

    record_metadata = RecordMetadata(record["logGroup"], record["logStream"])
    logs = []

    for log_event in record["logEvents"]:
        log_entry = transform_single_log_entry(log_event, batch_metadata, record_metadata)
        logs.append(log_entry)

    return logs


def transform_single_log_entry(log_event, batch_metadata, record_metadata):
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
    }

    if "timestamp" in log_event:
        parsed_record["timestamp"] = log_event["timestamp"]

    record = {
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
