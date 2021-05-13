import json
from dataclasses import dataclass
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

@dataclass
class Batch:
    serialized_json: str
    data_volume: int
    log_entries_count: int


def push_logs_to_dynatrace(logs: List[Dict], context: Context):
    batches = prepare_batches(logs, context)

    print(f"Prepared {len(batches)} batches")

    for batch in batches:
        context.sfm.batch_prepared(batch.log_entries_count, batch.data_volume)

    full_url = prepare_full_url(context.dt_url, LOGS_API_PATH)
    verify_SSL = context.verify_SSL

    headers = {
        "Authorization": f"Api-Token {context.dt_token}",
        "Content-Type": "application/json; charset=utf-8",
    }

    for i, batch in enumerate(batches):
        print(f"Pushing batch {i + 1} out of {len(batches)}")

        resp_status, _resp_body = http_client.perform_http_request_for_json(
            full_url, batch.serialized_json.encode(ENCODING), "POST", headers, verify_SSL, context
        )

        if resp_status == 413 or resp_status == 429:
            context.sfm.issue("throttle_response_code")
            raise CallThrottlingException(f"DT API throttling response, status code {resp_status}")
        elif resp_status > 299:
            context.sfm.issue("bad_response_code")
            raise CallOtherException(f"DT API bad response, status code {resp_status}")

        context.sfm.batch_delivered(batch.log_entries_count, batch.data_volume)


def prepare_full_url(dynatrace_url, path):
    if not dynatrace_url.startswith("http"):
        dynatrace_url = "https://" + dynatrace_url

    if dynatrace_url.endswith("/"):
        dynatrace_url = dynatrace_url[0:-1]

    if not path.startswith("/"):
        path = "/" + path

    return dynatrace_url + path


def prepare_batches(logs: List[Dict], context: Context) -> List[Batch]:
    batches: List[Batch] = []

    logs_for_next_batch: List[str] = []
    logs_for_next_batch_total_len = 0

    new_batch_len = 0

    for log_entry in logs:
        brackets_len = 2
        commas_len = len(logs_for_next_batch) - 1

        new_batch_len = logs_for_next_batch_total_len + brackets_len + commas_len

        ensure_fields_length(log_entry, context)

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
            serialized_batch = "[" + ",".join(logs_for_next_batch) + "]"
            batches.append(Batch(serialized_batch, new_batch_len, len(logs_for_next_batch)))

            logs_for_next_batch = []
            logs_for_next_batch_total_len = 0

        logs_for_next_batch.append(next_entry_serialized)
        logs_for_next_batch_total_len += next_entry_serialized_len

    if len(logs_for_next_batch) >= 1:
        # finalize last batch
        serialized_batch = "[" + ",".join(logs_for_next_batch) + "]"
        batches.append(Batch(serialized_batch, new_batch_len, len(logs_for_next_batch)))

    return batches


def ensure_fields_length(log_entry, context):
    for key, value in log_entry.items():
        if key == "content":
            ensure_content_length(log_entry, context)
        elif key == "severity":
            pass
        elif key == "timestamp":
            pass
        else:
            ensure_attribute_length(log_entry, key, value, context)


def ensure_content_length(log_entry, context):
    log_content = log_entry.get("content", "")
    log_content_len = len(log_content)
    if log_content_len > DYNATRACE_LOG_INGEST_CONTENT_MAX_LENGTH:
        context.sfm.log_content_trimmed()
        log_entry["content"] = log_content[0: DYNATRACE_LOG_INGEST_CONTENT_MAX_LENGTH]


def ensure_attribute_length(log_entry, key, value, context):
    attribute_value_len = len(value)
    if attribute_value_len > DYNATRACE_LOG_INGEST_ATTRIBUTE_MAX_LENGTH:
        context.sfm.log_attr_trimmed()
        log_entry[key] = value[0: DYNATRACE_LOG_INGEST_ATTRIBUTE_MAX_LENGTH]


class CallThrottlingException(Exception):
    pass


class CallOtherException(Exception):
    pass
