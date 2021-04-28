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

    ensure_credentials_provided(dt_token, dt_url)

    records = event['records']

    context = Context(function_name=lambda_context.function_name,
                      dt_url=dt_url,
                      dt_token=dt_token,
                      debug=debug_flag,
                      verify_SSL=verify_SSL)

    try:
        is_logs, plaintext_records = input_records_decoder.check_records_list_if_logs_end_decode(records)

        if not is_logs:
            raise Exception("Input not recognized as logs")

        main.process_log_request(plaintext_records, context, read_batch_metadata(event))

        return kinesis_data_transformation_response(records, TransformationResult.Ok)

    except CallThrottlingException:
        log_multiline_message("Call Throttling Exception, Kinesis batch will be marked as OK, but some data is dropped")
        return kinesis_data_transformation_response(records, TransformationResult.Ok)

    except Exception as e:
        log_error_with_stacktrace(e, "Exception caught in top-level handler")
        return kinesis_data_transformation_response(records, TransformationResult.ProcessingFailed)


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
