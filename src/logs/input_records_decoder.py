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
from typing import Tuple, List

from util.logging import log_error_with_stacktrace


def check_records_list_if_logs_end_decode(records) -> Tuple[bool, List[str]]:
    # returns: True, Records_list if content matches expected encoding
    # else returns: False, []
    # we expect following structure: [{"data": "BASE64_GZIPPED_LOGS"}, {"data": "BASE64_GZIPPED..."}]

    records_data = [record['data'] for record in records]

    if is_base64_with_gzip_header(records_data[0]):
        print("Recognized gzip record based on first two bytes")

        try:
            records_data_plaintext = [
                decode_and_unzip_single_record_data(record_data) for record_data in records_data
            ]
            print("Fully decoded logs payloads (base64 decode + ungzip)")
            return True, records_data_plaintext
        except Exception as e:
            log_error_with_stacktrace(e, "Ungzip failed")
            return False, []

    return False, []


def decode_and_unzip_single_record_data(record_data: str) -> str:
    data_binary = base64.b64decode(record_data)
    data_plaintext = gzip.decompress(data_binary).decode("utf-8")
    return data_plaintext


def is_base64_with_gzip_header(record_data: str) -> bool:
    if len(record_data) < 4:
        return False

    # first 4 characters in base64 decode into first 3 bytes
    start_chunk_b64 = record_data[0:4]
    start_chunk_bytes = base64.b64decode(start_chunk_b64)

    return start_chunk_bytes[0] == 0x1f and start_chunk_bytes[1] == 0x8b
