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

import ctypes
import hashlib
import struct

int64 = ctypes.c_int64


def meid_md5(entity_type: str, hashing_input: str):
    long_id = _legacy_entity_id_md5(hashing_input)
    identifier = _encode_me_identifier(entity_type, long_id)
    return identifier


def meid_murmurhash(entity_type: str, hashing_input: str) -> str:
    long_id = _murmurhash2_64A(hashing_input)
    identifier = _encode_me_identifier(entity_type, long_id)
    return identifier


def _legacy_entity_id_md5(hash_input: str) -> int:
    md5_digest = hashlib.md5(hash_input.encode("UTF-8"))
    md5_digest_bytes = md5_digest.digest()
    l1 = int.from_bytes(md5_digest_bytes[0:8], "big", signed=True)
    l2 = int.from_bytes(md5_digest_bytes[8:16], "big", signed=True)
    return l1 ^ l2


def _zfrs(num, shift):
    # Zero fill right shift.
    return int64((num & 0xFFFFFFFFFFFFFFFF) >> shift).value


def _murmurhash2_64A(data: str, seed=0xe17a1465) -> int:
    buf = bytearray(data.encode("UTF-8"))
    m = int64(0xc6a4a7935bd1e995).value
    r = 47
    offset = 0
    length = len(buf)

    h = int64(seed ^ ((length - offset) * m)).value

    k = 0

    while (length - offset) >= 8:
        k = struct.unpack_from('<q', buf, offset)[0]
        offset += 8

        k = int64(k * m).value
        k = int64(k ^ _zfrs(k, r)).value
        k = int64(k * m).value

        h = int64(h ^ k).value
        h = int64(h * m).value

    remaining = length - offset
    if remaining > 0:
        finish = bytearray(8)
        finish[:remaining] = buf[offset:]

        h = int64(h ^ struct.unpack_from('<q', finish)[0]).value
        h = int64(h * m).value

    h = int64(h ^ _zfrs(h, r)).value
    h = int64(h * m).value
    h = int64(h ^ _zfrs(h, r)).value
    return h


HEX_DIGITS = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'A', 'B', 'C', 'D', 'E', 'F']


def _encode_me_identifier(type_name: str, identifier: int) -> str:
    string_id = type_name + "-"
    i = 60
    while i >= 0:
        hex_digit_index = _zfrs(identifier, i) & 0xF
        string_id += HEX_DIGITS[hex_digit_index]
        i -= 4
    return string_id
