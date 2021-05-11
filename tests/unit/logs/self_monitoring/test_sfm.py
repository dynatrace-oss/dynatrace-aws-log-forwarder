from logs.self_monitoring.sfm import SelfMonitoringContext


def test_self_monitoring_context():
    sfm = SelfMonitoringContext("my-lambda-function")

    sfm.kinesis_record_age(5)
    sfm.kinesis_record_decoded(1000, 2000)

    sfm.single_record_transformed("logGroup1", 100, 1000)
    sfm.single_record_transformed("logGroup1", 100, 1000)
    sfm.single_record_transformed("logGroup2", 50, 2000)

    sfm.batch_prepared(100, 3000)
    sfm.batch_prepared(100, 3000)

    sfm.log_attr_trimmed()
    sfm.log_content_trimmed()
    sfm.log_content_trimmed()
    sfm.log_content_trimmed()

    sfm.logs_age(10,20,30)

    sfm.request_sent()
    sfm.batch_delivered(100, 3000)
    sfm.request_finished_with_status_code(200, 5)

    sfm.request_sent()
    sfm.issue("bad_status_code")
    sfm.request_finished_with_status_code(400, 2)

    metrics = sfm._generate_metrics()

    expected_metrics = [
        {
            'Dimensions': [{'Name': 'function_name', 'Value': 'my-lambda-function'}],
            'MetricName': 'Kinesis record age',
            'Unit': 'Seconds',
            'Values': [5]
        },
        {
            'Dimensions': [{'Name': 'function_name', 'Value': 'my-lambda-function'}],
            'MetricName': 'Kinesis record.data compressed size',
            'Unit': 'Bytes',
            'Values': [1000]
        },
        {
            'Dimensions': [{'Name': 'function_name', 'Value': 'my-lambda-function'}],
            'MetricName': 'Kinesis record.data decompressed size',
            'Unit': 'Bytes',
            'Values': [2000]
        },
        {
            'Dimensions': [{'Name': 'function_name', 'Value': 'my-lambda-function'},
                           {'Name': 'log_group', 'Value': 'logGroup1'}],
            'MetricName': 'Log entries by LogGroup',
            'Unit': 'None',
            'Value': 200
        },
        {
            'Dimensions': [{'Name': 'function_name', 'Value': 'my-lambda-function'},
                           {'Name': 'log_group', 'Value': 'logGroup2'}],
            'MetricName': 'Log entries by LogGroup',
            'Unit': 'None',
            'Value': 50
        },
        {
            'Dimensions': [{'Name': 'function_name', 'Value': 'my-lambda-function'},
                           {'Name': 'log_group', 'Value': 'logGroup1'}],
            'MetricName': 'Log content length by LogGroup',
            'Unit': 'None',
            'Value': 2000
        },
        {
            'Dimensions': [{'Name': 'function_name', 'Value': 'my-lambda-function'},
                           {'Name': 'log_group', 'Value': 'logGroup2'}],
            'MetricName': 'Log content length by LogGroup',
            'Unit': 'None',
            'Value': 2000
        },
        {
            'Dimensions': [{'Name': 'function_name', 'Value': 'my-lambda-function'}],
            'MetricName': 'Batches prepared',
            'Unit': 'None',
            'Value': 2
        },
        {
            'Dimensions': [{'Name': 'function_name', 'Value': 'my-lambda-function'}],
            'MetricName': 'Log entries prepared',
            'Unit': 'None',
            'Value': 200
        },
        {
            'Dimensions': [{'Name': 'function_name', 'Value': 'my-lambda-function'}],
            'MetricName': 'Data volume prepared',
            'Unit': 'Bytes',
            'Value': 6000
        },
        {
            'Dimensions': [{'Name': 'function_name', 'Value': 'my-lambda-function'}],
            'MetricName': 'Batches delivered',
            'Unit': 'None',
            'Value': 1
        },
        {
            'Dimensions': [{'Name': 'function_name', 'Value': 'my-lambda-function'}],
            'MetricName': 'Log entries delivered',
            'Unit': 'None',
            'Value': 100
        },
        {
            'Dimensions': [{'Name': 'function_name', 'Value': 'my-lambda-function'}],
            'MetricName': 'Data volume delivered',
            'Unit': 'Bytes',
            'Value': 3000
        },
        {
            'Dimensions': [{'Name': 'function_name', 'Value': 'my-lambda-function'},
                           {'Name': 'type', 'Value': 'bad_status_code'}],
            'MetricName': 'Issues',
            'Unit': 'None',
            'Value': 1
        },
        {
            'Dimensions': [{'Name': 'function_name', 'Value': 'my-lambda-function'}],
            'MetricName': 'Log content trimmed',
            'Unit': 'None',
            'Value': 3
        },
        {
            'Dimensions': [{'Name': 'function_name', 'Value': 'my-lambda-function'}],
            'MetricName': 'Log attr trimmed',
            'Unit': 'None',
            'Value': 1
        },
        {
            'Dimensions': [{'Name': 'function_name', 'Value': 'my-lambda-function'}],
            'MetricName': 'Log age min',
            'Unit': 'Seconds',
            'Value': 10
        },
        {
            'Dimensions': [{'Name': 'function_name', 'Value': 'my-lambda-function'}],
            'MetricName': 'Log age avg',
            'Unit': 'Seconds',
            'Value': 20
        },
        {
            'Dimensions': [{'Name': 'function_name', 'Value': 'my-lambda-function'}],
            'MetricName': 'Log age max',
            'Unit': 'Seconds',
            'Value': 30
        },
        {
            'Dimensions': [{'Name': 'function_name', 'Value': 'my-lambda-function'}],
            'MetricName': 'Requests sent',
            'Unit': 'None',
            'Value': 2
        },
        {
            'Dimensions': [{'Name': 'function_name', 'Value': 'my-lambda-function'}],
            'MetricName': 'Requests duration',
            'Unit': 'Seconds',
            'Values': [5, 2]
        },
        {
            'Dimensions': [{'Name': 'function_name', 'Value': 'my-lambda-function'},
                           {'Name': 'status_code', 'Value': '200'}],
            'MetricName': 'Requests status code count',
            'Unit': 'None',
            'Value': 1
        },
        {
            'Dimensions': [{'Name': 'function_name', 'Value': 'my-lambda-function'},
                           {'Name': 'status_code', 'Value': '400'}],
            'MetricName': 'Requests status code count',
            'Unit': 'None',
            'Value': 1}
    ]

    assert metrics == expected_metrics
