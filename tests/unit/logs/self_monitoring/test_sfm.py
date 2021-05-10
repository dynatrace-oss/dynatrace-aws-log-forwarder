from logs.self_monitoring.sfm import SelfMonitoringContext


def test_self_monitoring_context():
    sfm = SelfMonitoringContext()

    sfm.kinesis_record_age(5000)
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

    sfm.request_sent()
    sfm.batch_delivered(100, 3000)
    sfm.request_finished_with_status_code(200, 5)

    sfm.request_sent()
    sfm.issue("bad_status_code")
    sfm.request_finished_with_status_code(400, 2)

    metrics = sfm._generate_metrics()

    expected_metrics = [
        {
            'Dimensions': [],
            'MetricName': 'Kinesis record age',
            'Unit': 'Milliseconds',
            'Values': [5000]
        },
        {
            'Dimensions': [],
            'MetricName': 'Kinesis record.data compressed size',
            'Unit': 'Bytes',
            'Values': [1000]
        },
        {
            'Dimensions': [],
            'MetricName': 'Kinesis record.data decompressed size',
            'Unit': 'Bytes',
            'Values': [2000]
        },
        {
            'Dimensions': [{'Name': 'log_group', 'Value': 'logGroup1'}],
            'MetricName': 'Log entries by LogGroup',
            'Unit': 'None',
            'Value': 200
        },
        {
            'Dimensions': [{'Name': 'log_group', 'Value': 'logGroup2'}],
            'MetricName': 'Log entries by LogGroup',
            'Unit': 'None',
            'Value': 50
        },
        {
            'Dimensions': [{'Name': 'log_group', 'Value': 'logGroup1'}],
            'MetricName': 'Log content length by LogGroup',
            'Unit': 'None',
            'Value': 2000
        },
        {
            'Dimensions': [{'Name': 'log_group', 'Value': 'logGroup2'}],
            'MetricName': 'Log content length by LogGroup',
            'Unit': 'None',
            'Value': 2000
        },
        {
            "MetricName": "Batches prepared",
            "Dimensions": [],
            "Unit": "None",
            "Value": 2
        },
        {
            "MetricName": "Log entries prepared",
            "Dimensions": [],
            "Unit": "None",
            "Value": 200
        },
        {
            "MetricName": "Data volume prepared",
            "Dimensions": [],
            "Unit": "None",
            "Value": 6000
        },
        {
            "MetricName": "Batches delivered",
            "Dimensions": [],
            "Unit": "None",
            "Value": 1
        },
        {
            "MetricName": "Log entries delivered",
            "Dimensions": [],
            "Unit": "None",
            "Value": 100
        },
        {
            "MetricName": "Data volume delivered",
            "Dimensions": [],
            "Unit": "None",
            "Value": 3000
        },
        {
            "MetricName": "Issues",
            "Dimensions": [{"Name": "type", "Value": "bad_status_code"}],
            "Unit": "None",
            "Value": 1
        },
        {
            "MetricName": "Log content trimmed",
            "Dimensions": [],
            "Unit": "None",
            "Value": 3
        },
        {
            "MetricName": "Log attr trimmed",
            "Dimensions": [],
            "Unit": "None",
            "Value": 1
        },
        {
            "MetricName": "Requests sent",
            "Dimensions": [],
            "Unit": "None",
            "Value": 2
        },
        {
            "MetricName": "Requests duration",
            "Dimensions": [],
            "Unit": "Seconds",
            "Values": [5, 2]
        },
        {
            "MetricName": "Requests status code count",
            "Dimensions": [{"Name": "status_code", "Value": "200"}],
            "Unit": "None",
            "Value": 1
        },
        {
            "MetricName": "Requests status code count",
            "Dimensions": [{"Name": "status_code", "Value": "400"}],
            "Unit": "None",
            "Value": 1
        },
    ]

    assert metrics == expected_metrics

    # for expected_metric in expected_metrics:
    #     assert expected_metric in metrics

    # sfm.push_sfm_to_cloudwatch()
