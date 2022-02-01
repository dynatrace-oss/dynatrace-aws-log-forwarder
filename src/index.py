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

import os
from enum import Enum

from logs import input_records_decoder, main
from logs.logs_sender import CallThrottlingException
from logs.models.batch_metadata import BatchMetadata
from util.context import Context
from util.logging import log_error_with_stacktrace, log_multiline_message


def handler(event, lambda_context):
    debug_flag = os.environ.get('DEBUG', 'false') == 'true'
    dt_url = os.environ.get('DYNATRACE_ENV_URL')
    dt_token = os.environ.get('DYNATRACE_API_KEY')
    verify_SSL = os.environ.get('VERIFY_SSL', 'false') == 'true'
    cloud_log_forwarder = os.environ.get('CLOUD_LOG_FORWARDER', "")

    try:
        with open('version.txt') as versionFile:
            version = versionFile.readline()
    except Exception as e:
        version = "?"
        log_multiline_message(f"Couldn't read stack version. Exception: '{e}'.", "version-reading-exception")

    log_multiline_message("LOG FORWARDER version=" + version, "handler")

    ensure_credentials_provided(dt_token, dt_url)

    records = event['records']

    context = Context(function_name=lambda_context.function_name, dt_url=dt_url, dt_token=dt_token, debug=debug_flag,
                      verify_SSL=verify_SSL, cloud_log_forwarder=cloud_log_forwarder)

    try:
        is_logs, plaintext_records = input_records_decoder.check_records_list_if_logs_end_decode(records, context)

        if not is_logs:
            raise Exception("Input not recognized as logs")

        main.process_log_request(plaintext_records, context, read_batch_metadata(event))
        result = TransformationResult.Ok

    except CallThrottlingException:
        log_multiline_message("Call Throttling Exception, Kinesis batch will be marked as OK, but some data is dropped",
                              "call-throttling-exception")
        result = TransformationResult.Ok

    except Exception as e:
        log_error_with_stacktrace(e, "Exception caught in top-level handler",
                                  "top-level-handler-exception")
        result = TransformationResult.ProcessingFailed

    try:
        context.sfm.push_sfm_to_cloudwatch()
    except Exception as e:
        log_error_with_stacktrace(e, "SelfMonitoring push to Cloudwatch failed",
                                   "sfm-push-exception")

    return kinesis_data_transformation_response(records, result)


def read_batch_metadata(event):
    # example: arn:aws:firehose:us-east-1:444652832050:deliverystream/b-FirehoseLogStreams-lbcTAGyNE8hz
    arn = event['deliveryStreamArn']
    arn_parts = arn.split(':')

    partition = arn_parts[1]
    account_id = arn_parts[4]
    region = event['region']

    batch_metadata = BatchMetadata(account_id, region, partition)
    return batch_metadata


def ensure_credentials_provided(dt_token, dt_url):
    if not dt_url:
        raise Exception("DYNATRACE_ENV_URL not provided")
    if not dt_token:
        raise Exception("DYNATRACE_API_KEY not provided")


class TransformationResult(Enum):
    # Kinesis Firehose Data Transformation Result (per record)
    Ok = 0
    Dropped = 1
    ProcessingFailed = 2


def kinesis_data_transformation_response(input_records, result_for_all_records: TransformationResult):
    print("Kinesis Data Transformation Result for all records is", result_for_all_records)

    output_records = []

    for input_record in input_records:
        output_records.append(
            {
                "recordId": input_record["recordId"],
                "result": result_for_all_records.name,
                "data": input_record["data"],
            }
        )

    return {
        "records": output_records
    }
