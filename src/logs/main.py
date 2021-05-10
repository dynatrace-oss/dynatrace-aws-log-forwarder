import statistics
import time
from typing import List, Dict

from logs.logs_sender import push_logs_to_dynatrace
from logs.models.batch_metadata import BatchMetadata
from logs.transformation import extract_dt_logs_from_single_record
from util.context import Context
from util.logging import debug_log_multiline_message


def process_log_request(decoded_records: List[str], context: Context, batch_metadata: BatchMetadata):
    all_logs: List[Dict] = []

    for record in decoded_records:
        all_logs.extend(extract_dt_logs_from_single_record(record, batch_metadata, context))

    print(f"Extracted {len(all_logs)} log entries from {len(decoded_records)} records given")

    debug_log_multiline_message("Log entries to be sent to DT: " + str(all_logs), context)

    sfm_report_logs_age(all_logs, context)

    push_logs_to_dynatrace(all_logs, context)


def sfm_report_logs_age(logs, context):
    sample_every_nth = 20
    sampling_indexes = range(0, len(logs), sample_every_nth)

    log_ages_ms = []
    timestamp_now_ms = round(time.time() * 1000)

    for i in sampling_indexes:
        log = logs[i]
        try:
            log_timestamp_ms = log['timestamp']
            age_ms = int(timestamp_now_ms) - log_timestamp_ms
            log_ages_ms.append(age_ms)
        except Exception as e:
            pass

    if len(log_ages_ms) >= 1:
        context.sfm.avg_log_age(statistics.mean(log_ages_ms))

    print(f"Extracted {len(log_ages_ms)} timestamp samples from {len(logs)} logs, sampling {sample_every_nth}")
