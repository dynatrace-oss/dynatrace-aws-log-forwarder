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

    debug_log_multiline_message("Log entries to be sent to DT: " + str(all_logs), context,
                                "logs-send-details")

    sfm_report_logs_age(all_logs, context)

    push_logs_to_dynatrace(all_logs, context)


def sfm_report_logs_age(logs, context):
    timestamp_now_ms = round(time.time() * 1000)

    log_ages_sec = []

    for log in logs:
        try:
            log_timestamp_ms = log['timestamp']
            log_age_ms = int(timestamp_now_ms) - log_timestamp_ms
            log_age_sec = log_age_ms / 1000
            log_ages_sec.append(log_age_sec)
        except Exception:
            pass

    if len(log_ages_sec) >= 1:
        log_age_min = min(log_ages_sec)
        log_age_avg = statistics.mean(log_ages_sec)
        log_age_max = max(log_ages_sec)
        context.sfm.logs_age(log_age_min, log_age_avg, log_age_max)
