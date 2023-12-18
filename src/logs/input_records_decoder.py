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

import base64
import gzip
import time
from typing import Tuple, List

from util.context import Context
from util.logging import log_error_with_stacktrace


def check_records_list_if_logs_end_decode(records, context: Context) -> Tuple[bool, List[str]]:
    # returns: True, Records_list if content matches expected encoding
    # else returns: False, []
    # we expect following structure: [{"data": "BASE64_GZIPPED_LOGS"}, {"data": "BASE64_GZIPPED..."}]

    records_data = [record['data'] for record in records]

    sfm_report_kinesis_records_age(records, context)

    if is_base64_with_gzip_header(records_data[0]):
        print("Recognized gzip record based on first two bytes")

        try:
            records_data_plaintext = [
                decode_and_unzip_single_record_data(record_data, context) for record_data in records_data
            ]
            print("Fully decoded logs payloads (base64 decode + ungzip)")
            return True, records_data_plaintext
        except Exception as e:
            log_error_with_stacktrace(e, "Ungzip failed",
                                      "ungzip-failed-exception")
            return False, []

    return False, []


def decode_and_unzip_single_record_data(record_data: str, context) -> str:
    data_binary = base64.b64decode(record_data)
    decoded_record_data = gzip.decompress(data_binary).decode("utf-8")

    len_incoming = len(record_data.encode("UTF-8"))
    len_decoded = len(decoded_record_data.encode("UTF-8"))

    context.sfm.kinesis_record_decoded(len_incoming, len_decoded)

    return decoded_record_data


def is_base64_with_gzip_header(record_data: str) -> bool:
    if len(record_data) < 4:
        return False

    # first 4 characters in base64 decode into first 3 bytes
    start_chunk_b64 = record_data[0:4]
    start_chunk_bytes = base64.b64decode(start_chunk_b64)

    return start_chunk_bytes[0] == 0x1f and start_chunk_bytes[1] == 0x8b


def sfm_report_kinesis_records_age(records, context):
    try:
        timestamp_now_sec = time.time()

        for record in records:
            kinesis_record_timestamp_ms = record['approximateArrivalTimestamp']
            kinesis_record_timestamp_sec = int(kinesis_record_timestamp_ms / 1000)
            age_sec = timestamp_now_sec - kinesis_record_timestamp_sec
            context.sfm.kinesis_record_age(age_sec)

    except Exception as e:
        log_error_with_stacktrace(e, "Failed to calculate Kinesis Record Delay Self Monitoring",
                                  "sfm-record-delay-calc-exception")

class BadSchemaError(Exception):
    '''BadSchemaError is raised when the received logs do not meet the expected format.'''

    def __init__(self, erroneous_field: str) -> None:
        message = f"""Lambda was called with an event of unrecognized schema.
        Make sure you have configured everything correctly. Unexpected problem happened when trying to parse field: {erroneous_field}
        """
        super().__init__(message)
