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
from typing import List, Dict

from util import http_client, logging
from util.context import Context

ENCODING = "utf-8"

LOGS_API_PATH = "/api/v2/logs/ingest"

DYNATRACE_LOG_INGEST_CONTENT_MAX_LENGTH = 8192
DYNATRACE_LOG_INGEST_ATTRIBUTE_MAX_LENGTH = 250
DYNATRACE_LOG_INGEST_REQUEST_MAX_SIZE = 1048576 # 1MB
DYNATRACE_LOG_INGEST_MAX_RECORD_AGE = 86340 # 1 day
DYNATRACE_LOG_INGEST_MAX_ENTRIES_COUNT = 5000

def push_logs_to_dynatrace(logs: List[Dict], context: Context):
    serialized_batches = prepare_serialized_batches(logs)

    print(f"Prepared {len(serialized_batches)} batches")

    full_url = prepare_full_url(context.dt_url, LOGS_API_PATH)
    verify_SSL = context.verify_SSL

    headers = {
        "Authorization": f"Api-Token {context.dt_token}",
        "Content-Type": "application/json; charset=utf-8",
    }

    for i, batch in enumerate(serialized_batches):
        print(f"Pushing batch {i + 1} out of {len(serialized_batches)}")

        resp_status, _resp_body = http_client.perform_http_request_for_json(
            full_url, batch.encode(ENCODING), "POST", headers, verify_SSL
        )

        if resp_status == 413 or resp_status == 429:
            raise CallThrottlingException(f"DT API throttling response, status code {resp_status}")
        elif resp_status > 299:
            raise CallOtherException(f"DT API bad response, status code {resp_status}")


def prepare_full_url(dynatrace_url, path):
    if not dynatrace_url.startswith("http"):
        dynatrace_url = "https://" + dynatrace_url

    if dynatrace_url.endswith("/"):
        dynatrace_url = dynatrace_url[0:-1]

    if not path.startswith("/"):
        path = "/" + path

    return dynatrace_url + path


def prepare_serialized_batches(logs: List[Dict]) -> List[str]:
    batches: List[str] = []

    logs_for_next_batch: List[str] = []
    logs_for_next_batch_total_len = 0

    for log_entry in logs:
        brackets_len = 2
        commas_len = len(logs_for_next_batch) - 1

        new_batch_len = logs_for_next_batch_total_len + brackets_len + commas_len

        ensure_fields_length(log_entry)

        next_entry_serialized = json.dumps(log_entry)
        next_entry_serialized_len = len(next_entry_serialized.encode(ENCODING))

        if next_entry_serialized_len > DYNATRACE_LOG_INGEST_REQUEST_MAX_SIZE:
            # shouldn't happen as we are already truncating the content field, but just for safety
            logging.log_multiline_message(f"Dropping entry, as it's size is {next_entry_serialized_len}, "
                                          f"bigger than max entry size: {DYNATRACE_LOG_INGEST_REQUEST_MAX_SIZE}")

        batch_length_if_added_entry = new_batch_len + 1 + next_entry_serialized_len  # +1 is for comma
        batch_entries_if_added_entry = len(logs_for_next_batch) + 1

        if batch_length_if_added_entry > DYNATRACE_LOG_INGEST_REQUEST_MAX_SIZE or \
                batch_entries_if_added_entry > DYNATRACE_LOG_INGEST_MAX_ENTRIES_COUNT:
            # would overflow limit, close batch and prepare new
            batch = "[" + ",".join(logs_for_next_batch) + "]"
            batches.append(batch)

            logs_for_next_batch = []
            logs_for_next_batch_total_len = 0

        logs_for_next_batch.append(next_entry_serialized)
        logs_for_next_batch_total_len += next_entry_serialized_len

    if len(logs_for_next_batch) >= 1:
        # finalize last batch
        batch = "[" + ",".join(logs_for_next_batch) + "]"
        batches.append(batch)

    return batches


def ensure_fields_length(log_entry):
    for key, value in log_entry.items():
        if key == "content":
            ensure_content_length(log_entry)
        elif key == "severity":
            pass
        elif key == "timestamp":
            pass
        else:
            ensure_attribute_length(log_entry, key, value)


def ensure_content_length(log_entry):
    log_content = log_entry.get("content", "")
    log_content_len = len(log_content)
    if log_content_len > DYNATRACE_LOG_INGEST_CONTENT_MAX_LENGTH:
        # placeholder for APM-290579 Implement self-monitoring
        # dynatrace-azure-logs-ingest/logs_ingest/main.py:117
        # self_monitoring.too_long_content_size.append(log_content_len)

        log_entry["content"] = log_content[0: DYNATRACE_LOG_INGEST_CONTENT_MAX_LENGTH]


def ensure_attribute_length(log_entry, key, value):
    attribute_value_len = len(value)
    if attribute_value_len > DYNATRACE_LOG_INGEST_ATTRIBUTE_MAX_LENGTH:
        log_entry[key] = value[0: DYNATRACE_LOG_INGEST_ATTRIBUTE_MAX_LENGTH]


class CallThrottlingException(Exception):
    pass


class CallOtherException(Exception):
    pass
