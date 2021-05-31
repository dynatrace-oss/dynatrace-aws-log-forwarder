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

from collections import defaultdict
from typing import Union

import boto3


class SelfMonitoringContext:

    def __init__(self, function_name):
        self._function_name = function_name

        self._kinesis_records_age = []
        self._record_data_compressed_size = []
        self._record_data_decompressed_size = []

        self._log_entries_by_log_group = defaultdict(lambda: 0)
        self._log_content_len_by_log_group = defaultdict(lambda: 0)

        self._batches_prepared = 0
        self._log_entries_prepared = 0
        self._data_volume_prepared = 0

        self._batches_delivered = 0
        self._log_entries_delivered = 0
        self._data_volume_delivered = 0

        self._issue_count_by_type = defaultdict(lambda: 0)

        self._log_content_trimmed = 0
        self._log_attr_trimmed = 0

        self._logs_age_min_sec = None
        self._logs_age_avg_sec = None
        self._logs_age_max_sec = None

        self._requests_sent = 0
        self._requests_durations_ms = []
        self._requests_count_by_status_code = defaultdict(lambda: 0)

    def kinesis_record_age(self, age_sec):
        self._kinesis_records_age.append(age_sec)

    def kinesis_record_decoded(self, record_data_compressed_size, record_data_decompressed_size):
        self._record_data_compressed_size.append(record_data_compressed_size)
        self._record_data_decompressed_size.append(record_data_decompressed_size)

    def single_record_transformed(self, log_group, log_entries_count, log_content_len):
        self._log_entries_by_log_group[log_group] += log_entries_count
        self._log_content_len_by_log_group[log_group] += log_content_len

    def batch_prepared(self, log_entries_count, data_volume):
        self._batches_prepared += 1
        self._log_entries_prepared += log_entries_count
        self._data_volume_prepared += data_volume

    def batch_delivered(self, log_entries_count, data_volume):
        self._batches_delivered += 1
        self._log_entries_delivered += log_entries_count
        self._data_volume_delivered += data_volume

    def issue(self, what_issue):
        self._issue_count_by_type[what_issue] += 1
        print("SFM: issue registered, type " + what_issue)

    def log_content_trimmed(self):
        self._log_content_trimmed += 1

    def log_attr_trimmed(self):
        self._log_attr_trimmed += 1

    def logs_age(self, logs_age_min_sec, logs_age_avg_sec, logs_age_max_sec):
        self._logs_age_min_sec = logs_age_min_sec
        self._logs_age_avg_sec = logs_age_avg_sec
        self._logs_age_max_sec = logs_age_max_sec

    def request_sent(self):
        self._requests_sent += 1

    def request_finished_with_status_code(self, status_code, duration_ms):
        self._requests_count_by_status_code[status_code] += 1
        self._requests_durations_ms.append(duration_ms)

    def _generate_metrics(self):
        metrics = []

        common_dimensions = [{
            "Name": "function_name",
            "Value": self._function_name,
        }]

        metrics.append(_prepare_cloudwatch_metric(
            "Kinesis record age", self._kinesis_records_age, "Seconds", common_dimensions))
        metrics.append(_prepare_cloudwatch_metric(
            "Kinesis record.data compressed size", self._record_data_compressed_size, "Bytes", common_dimensions))
        metrics.append(_prepare_cloudwatch_metric(
            "Kinesis record.data decompressed size", self._record_data_decompressed_size, "Bytes", common_dimensions))

        for log_group, log_entries_count in self._log_entries_by_log_group.items():
            metrics.append(_prepare_cloudwatch_metric(
                "Log entries by LogGroup", log_entries_count, "None",
                common_dimensions + [{"Name": "log_group", "Value": log_group}]
            ))

        for log_group, log_content_len in self._log_content_len_by_log_group.items():
            metrics.append(_prepare_cloudwatch_metric(
                "Log content length by LogGroup", log_content_len, "None",
                common_dimensions + [{"Name": "log_group", "Value": log_group}]
            ))

        metrics.append(_prepare_cloudwatch_metric(
            "Batches prepared", self._batches_prepared, "None", common_dimensions))
        metrics.append(_prepare_cloudwatch_metric(
            "Log entries prepared", self._log_entries_prepared, "None", common_dimensions))
        metrics.append(_prepare_cloudwatch_metric(
            "Data volume prepared", self._data_volume_prepared, "Bytes", common_dimensions))

        metrics.append(_prepare_cloudwatch_metric(
            "Batches delivered", self._batches_delivered, "None", common_dimensions))
        metrics.append(_prepare_cloudwatch_metric(
            "Log entries delivered", self._log_entries_delivered, "None", common_dimensions))
        metrics.append(_prepare_cloudwatch_metric(
            "Data volume delivered", self._data_volume_delivered, "Bytes", common_dimensions))

        for issue, count in self._issue_count_by_type.items():
            metrics.append(_prepare_cloudwatch_metric(
                "Issues", count, "None",
                common_dimensions + [{"Name": "type", "Value": issue}]
            ))

        metrics.append(_prepare_cloudwatch_metric(
            "Log content trimmed", self._log_content_trimmed, "None", common_dimensions))
        metrics.append(_prepare_cloudwatch_metric(
            "Log attr trimmed", self._log_attr_trimmed, "None", common_dimensions))

        if self._logs_age_min_sec:
            metrics.append(_prepare_cloudwatch_metric(
                "Log age min", self._logs_age_min_sec, "Seconds", common_dimensions))
            metrics.append(_prepare_cloudwatch_metric(
                "Log age avg", self._logs_age_avg_sec, "Seconds", common_dimensions))
            metrics.append(_prepare_cloudwatch_metric(
                "Log age max", self._logs_age_max_sec, "Seconds", common_dimensions))

        metrics.append(_prepare_cloudwatch_metric(
            "Requests sent", self._requests_sent, "None", common_dimensions))
        if self._requests_durations_ms:
            metrics.append(_prepare_cloudwatch_metric(
                "Requests duration", self._requests_durations_ms, "Milliseconds", common_dimensions))

        for status_code, count in self._requests_count_by_status_code.items():
            metrics.append(_prepare_cloudwatch_metric(
                "Requests status code count", count, "None",
                common_dimensions + [{"Name": "status_code", "Value": str(status_code)}]
            ))

        return metrics

    def push_sfm_to_cloudwatch(self):
        metrics = self._generate_metrics()
        cloudwatch = boto3.client('cloudwatch')
        try:
            for i in range(0, len(metrics), 20):
                metrics_batch = metrics[i:(i + 20)]
                cloudwatch.put_metric_data(MetricData=metrics_batch, Namespace='DT/LogsStreaming')
        except Exception as e:
            print("Print metrics on SFM push failure: " + str(metrics))
            raise e


def _prepare_cloudwatch_metric(metric_name, value: Union[int, float, list], unit, dimensions) -> dict:
    cw_metric = {
        'MetricName': metric_name,
        'Dimensions': dimensions,
        'Unit': unit,
    }

    if isinstance(value, list):
        cw_metric["Values"] = value
    else:
        cw_metric["Value"] = value

    return cw_metric
