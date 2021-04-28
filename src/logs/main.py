from typing import List, Dict

from logs.logs_sender import push_logs_to_dynatrace
from logs.models.batch_metadata import BatchMetadata
from logs.transformation import extract_dt_logs_from_single_record
from util.context import Context
from util.logging import debug_log_multiline_message


def process_log_request(decoded_records: List[str], context: Context, batch_metadata: BatchMetadata):
    all_logs: List[Dict] = []

    for record in decoded_records:
        all_logs.extend(extract_dt_logs_from_single_record(record, batch_metadata))

    print(f"Extracted {len(all_logs)} log entries from {len(decoded_records)} records given")

    debug_log_multiline_message("Log entries to be sent to DT: " + str(all_logs), context)

    push_logs_to_dynatrace(all_logs, context)
