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
import random
from unittest import TestCase

from logs import logs_sender
from util.context import Context

DYNATRACE_LOG_INGEST_REQUEST_MAX_SIZE = 1048576

log_message = "WALTHAM, Mass.--(BUSINESS WIRE)-- Software intelligence company Dynatrace (NYSE: DT) announced today its entry into the cloud application security market with the addition of a new module to its industry-leading Software Intelligence Platform. The Dynatrace® Application Security Module provides continuous runtime application self-protection (RASP) capabilities for applications in production as well as preproduction and is optimized for Kubernetes architectures and DevSecOps approaches. This module inherits the automation, AI, scalability, and enterprise-grade robustness of the Dynatrace® Software Intelligence Platform and extends it to modern cloud RASP use cases. Dynatrace customers can launch this module with the flip of a switch, empowering the world’s leading organizations currently using the Dynatrace platform to immediately increase security coverage and precision.;"


def create_log_entry_with_random_len_msg(min_length = 1, max_length = len(log_message)):
    min_length = max(min_length, 1)
    max_length = min(max_length, len(log_message))

    random_len = random.randint(min_length, max_length)
    random_len_str = log_message[0: random_len]

    return {
        'content': random_len_str,
        'cloud.provider': 'AWS',
        'severity': 'INFO'
    }


class Test(TestCase):

    def test_prepare_serialized_batches(self):
        context = Context("function-name", "dt-url", "dt-token", False, False, "log.forwarder",
                          logs_sender.DYNATRACE_LOG_INGEST_CONTENT_DEFAULT_MAX_LENGTH)
        how_many_logs = 20000
        logs = [create_log_entry_with_random_len_msg() for x in range(how_many_logs)]

        batches = logs_sender.prepare_batches(logs, context)

        self.assertGreaterEqual(len(batches), 1)

        entries_in_batches = 0

        for batch in batches:
            self.assertTrue(len(batch.serialized_json) <= DYNATRACE_LOG_INGEST_REQUEST_MAX_SIZE)
            entries_in_batches += len(json.loads(batch.serialized_json))

        self.assertEqual(entries_in_batches, how_many_logs)

        logs_lengths = [len(log) for log in logs]
        logs_total_length = sum(logs_lengths)

        batches_lengths = [len(batch.serialized_json) for batch in batches]
        batches_total_length = sum(batches_lengths)

        self.assertGreater(batches_total_length, logs_total_length)

    def test_request_and_content_length(self):
        context = Context("function-name", "dt-url", "dt-token", False, False, "log.forwarder", 50)
        how_many_logs = 10
        logs = [create_log_entry_with_random_len_msg(750, 900) for x in range(how_many_logs)]

        logs_sender.DYNATRACE_LOG_INGEST_REQUEST_MAX_SIZE = 115

        batches = logs_sender.prepare_batches(logs, context)

        self.assertGreaterEqual(len(batches), 1)

        entries_in_batches = 0

        for batch in batches:
            entries = json.loads(batch.serialized_json)

            for entry in entries:
                content_len = len(entry["content"])
                self.assertTrue(content_len == 50)
                self.assertTrue(content_len <= context.max_log_length)
                self.assertTrue(entry["content"] == 'WALTHAM, Mass.--(BUSINESS WIRE)-- Softw[TRUNCATED]')

            self.assertTrue(len(batch.serialized_json) <= logs_sender.DYNATRACE_LOG_INGEST_REQUEST_MAX_SIZE)

            entries_in_this_batch = len(entries)
            self.assertTrue(entries_in_this_batch <= 1)

            entries_in_batches += entries_in_this_batch

        self.assertEqual(entries_in_batches, how_many_logs)

        logs_lengths = [len(log) for log in logs]
        logs_total_length = sum(logs_lengths)

        batches_lengths = [len(batch.serialized_json) for batch in batches]
        batches_total_length = sum(batches_lengths)

        self.assertGreater(batches_total_length, logs_total_length)

    def test_entries_in_batch(self):
        context = Context("function-name", "dt-url", "dt-token", False, False, "log.forwarder", 500)
        how_many_logs = 20000
        logs = [create_log_entry_with_random_len_msg() for x in range(how_many_logs)]

        logs_sender.DYNATRACE_LOG_INGEST_MAX_ENTRIES_COUNT = 2
        batches = logs_sender.prepare_batches(logs, context)

        self.assertGreaterEqual(len(batches), 1)

        entries_in_batches = 0

        for batch in batches:
            self.assertTrue(len(batch.serialized_json) <= logs_sender.DYNATRACE_LOG_INGEST_REQUEST_MAX_SIZE)

            entries_in_this_batch = len(json.loads(batch.serialized_json))
            self.assertTrue(entries_in_this_batch <= logs_sender.DYNATRACE_LOG_INGEST_MAX_ENTRIES_COUNT)
            entries_in_batches += entries_in_this_batch

        self.assertEqual(entries_in_batches, how_many_logs)

        logs_lengths = [len(log) for log in logs]
        logs_total_length = sum(logs_lengths)

        batches_lengths = [len(batch.serialized_json) for batch in batches]
        batches_total_length = sum(batches_lengths)

        self.assertGreater(batches_total_length, logs_total_length)

    def test_trim_fields(self):
        context = Context("function-name", "dt-url", "dt-token", False, False, "log.forwarder", 600)
        string_with_900_chars = log_message

        # sanity checks
        self.assertTrue(len(string_with_900_chars) > logs_sender.DYNATRACE_LOG_INGEST_ATTRIBUTE_MAX_LENGTH)
        self.assertTrue(len(string_with_900_chars) > context.max_log_length)

        log_entry = create_log_entry_with_random_len_msg()
        log_entry["timestamp"] = string_with_900_chars
        log_entry["content"] = string_with_900_chars
        log_entry["severity"] = string_with_900_chars
        log_entry["cloud.provider"] = string_with_900_chars
        log_entry["aws.service"] = string_with_900_chars
        log_entry["someMetadataYetUnknown"] = string_with_900_chars

        # test
        logs_sender.ensure_fields_length(log_entry, context)

        self.assertTrue(log_entry["timestamp"] == string_with_900_chars)
        self.assertTrue(log_entry["severity"] == string_with_900_chars)
        self.assertTrue(len(log_entry["content"]) == context.max_log_length)
        self.assertTrue(len(log_entry["cloud.provider"]) == logs_sender.DYNATRACE_LOG_INGEST_ATTRIBUTE_MAX_LENGTH)
        self.assertTrue(len(log_entry["aws.service"]) == logs_sender.DYNATRACE_LOG_INGEST_ATTRIBUTE_MAX_LENGTH)
        self.assertTrue(len(log_entry["someMetadataYetUnknown"]) == logs_sender.DYNATRACE_LOG_INGEST_ATTRIBUTE_MAX_LENGTH)


    def test_prepare_full_url(self):

        expected = "https://3.3.3.3:9999/e/123/api/v1/logs/ingest"

        self.assertEqual(logs_sender.prepare_full_url("3.3.3.3:9999", "/e/123/api/v1/logs/ingest"), expected)
        self.assertEqual(logs_sender.prepare_full_url("https://3.3.3.3:9999", "/e/123/api/v1/logs/ingest"), expected)
        self.assertEqual(logs_sender.prepare_full_url("https://3.3.3.3:9999/", "/e/123/api/v1/logs/ingest"), expected)
        self.assertEqual(logs_sender.prepare_full_url("https://3.3.3.3:9999/", "/e/123/api/v1/logs/ingest"), expected)
        self.assertEqual(logs_sender.prepare_full_url("https://3.3.3.3:9999/e/123", "/api/v1/logs/ingest"), expected)
        self.assertEqual(logs_sender.prepare_full_url("3.3.3.3:9999/e/123", "/api/v1/logs/ingest"), expected)
        self.assertEqual(logs_sender.prepare_full_url("3.3.3.3:9999/e/123", "api/v1/logs/ingest"), expected)

        expected = "https://jxw.dynatrace.com/e/123/api/v1/logs/ingest"

        self.assertEqual(logs_sender.prepare_full_url("jxw.dynatrace.com", "/e/123/api/v1/logs/ingest"), expected)
        self.assertEqual(logs_sender.prepare_full_url("https://jxw.dynatrace.com", "/e/123/api/v1/logs/ingest"), expected)
        self.assertEqual(logs_sender.prepare_full_url("https://jxw.dynatrace.com/", "/e/123/api/v1/logs/ingest"), expected)
        self.assertEqual(logs_sender.prepare_full_url("https://jxw.dynatrace.com/", "/e/123/api/v1/logs/ingest"), expected)
        self.assertEqual(logs_sender.prepare_full_url("https://jxw.dynatrace.com/e/123", "/api/v1/logs/ingest"), expected)
        self.assertEqual(logs_sender.prepare_full_url("jxw.dynatrace.com/e/123", "/api/v1/logs/ingest"), expected)
        self.assertEqual(logs_sender.prepare_full_url("jxw.dynatrace.com/e/123", "api/v1/logs/ingest"), expected)
