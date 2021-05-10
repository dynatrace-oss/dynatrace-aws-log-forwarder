from collections import defaultdict
from typing import Union

import boto3

cloudwatch = boto3.client('cloudwatch')


class SelfMonitoringContext:
    _function_name = None

    _kinesis_records_age = []
    _record_data_compressed_size = []
    _record_data_decompressed_size = []

    _log_entries_by_log_group = defaultdict(lambda: 0)
    _log_content_len_by_log_group = defaultdict(lambda: 0)

    _batches_prepared = 0
    _log_entries_prepared = 0
    _data_volume_prepared = 0

    _batches_delivered = 0
    _log_entries_delivered = 0
    _data_volume_delivered = 0

    _issue_count_by_type = defaultdict(lambda: 0)

    _log_content_trimmed = 0
    _log_attr_trimmed = 0

    _avg_logs_age_ms = 0

    _requests_sent = 0
    _requests_durations_sec = []
    _requests_count_by_status_code = defaultdict(lambda: 0)

    def __init__(self, function_name):
        self._function_name = function_name

    def kinesis_record_age(self, age_ms):
        self._kinesis_records_age.append(age_ms)

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

    def log_content_trimmed(self):
        self._log_content_trimmed += 1

    def log_attr_trimmed(self):
        self._log_attr_trimmed += 1

    def avg_log_age(self, age_ms):
        self._avg_logs_age_ms = age_ms

    def request_sent(self):
        self._requests_sent += 1

    def request_finished_with_status_code(self, status_code, duration_sec):
        self._requests_count_by_status_code[status_code] += 1
        self._requests_durations_sec.append(duration_sec)

    def _generate_metrics(self):
        metrics = []

        common_dimensions = [{
            "Name": "function_name",
            "Value": self._function_name,
        }]

        metrics.append(_prepare_cloudwatch_metric(
            "Kinesis record age", self._kinesis_records_age, "Milliseconds", common_dimensions))
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

        metrics.append(_prepare_cloudwatch_metric(
            "Log age average", self._avg_logs_age_ms, "Milliseconds", common_dimensions))

        metrics.append(_prepare_cloudwatch_metric(
            "Requests sent", self._requests_sent, "None", common_dimensions))
        metrics.append(_prepare_cloudwatch_metric(
            "Requests duration", self._requests_durations_sec, "Seconds", common_dimensions))

        for status_code, count in self._requests_count_by_status_code.items():
            metrics.append(_prepare_cloudwatch_metric(
                "Requests status code count", count, "None",
                common_dimensions + [{"Name": "status_code", "Value": str(status_code)}]
            ))

        return metrics

    def push_sfm_to_cloudwatch(self):
        metrics = self._generate_metrics()
        print(metrics)
        cloudwatch.put_metric_data(MetricData=metrics, Namespace='DT/LogsStreamingDEV2')


def _prepare_cloudwatch_metric(metric_name, value: Union[int, float, list], unit, dimensions) -> dict:
    cw_metric = {
        'MetricName': metric_name,
        'Dimensions': dimensions,
        'Unit': unit,
    }

    if type(value) is list:
        cw_metric["Values"] = value
    else:
        cw_metric["Value"] = value

    return cw_metric
