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

from logs.metadata_engine import me_id, jmespath

jmes_custom_functions = jmespath.MappingCustomFunctions()

def test_meid_in_credentials_v1_elb():
    dns_name = "internal-a016dbd362e6d4da88e1c38597c3c2ec-638512738.us-east-1.elb.amazonaws.com"
    real_meid_from_dt_cluster="ELASTIC_LOAD_BALANCER-8528390864056438"

    meid = jmes_custom_functions._func_dt_meid_elb_v1(dns_name)
    # assert meid == real_meid_from_dt_cluster
    # no real example - uncomment when confiremed

def test_meid_in_credentials_v1_nlb():
    arn = "arn:aws:elasticloadbalancing:us-east-1:908047316593:loadbalancer/net/mawo-lb/15849cc195988fcd"
    real_meid_from_dt_cluster="AWS_NETWORK_LOAD_BALANCER-EF0EC97D1EB86C93"

    meid = jmes_custom_functions._func_dt_meid_nlb_v1(arn)
    assert meid == real_meid_from_dt_cluster

def test_meid_in_credentials_v1_alb():
    arn = "arn:aws:elasticloadbalancing:us-east-1:908047316593:loadbalancer/app/awseb-AWSEB-1PVCR48G91GIH/9468cad8f10dd41f"
    real_meid_from_dt_cluster="AWS_APPLICATION_LOAD_BALANCER-4F6A35C7A333D2A9"

    meid = jmes_custom_functions._func_dt_meid_alb_v1(arn)
    assert meid == real_meid_from_dt_cluster

def test_meid_in_credentials_v1_auto_scaling_group():
    arn = "arn:aws:autoscaling:us-east-1:908047316593:autoScalingGroup:eae95707-f82d-44c8-ac1a-ab8c0edb73c8:autoScalingGroupName/awseb-e-zyzwkdfndi-stack-AWSEBAutoScalingGroup-RNJ3TG08OKTM"
    real_meid_from_dt_cluster="AUTO_SCALING_GROUP-7F3716C2F8B9F010"

    meid = jmes_custom_functions._func_dt_meid_auto_scaling_group_v1(arn)
    assert meid == real_meid_from_dt_cluster

def test_meid_in_credentials_v1_dynamo_db():
    table_name = "METRIC_TEST_2"
    region = "us-west-1"
    real_meid_from_dt_cluster="DYNAMO_DB_TABLE-B92738E1BDB27DC3"

    meid = jmes_custom_functions._func_dt_meid_dynamo_db_v1(table_name, region)
    assert meid == real_meid_from_dt_cluster

def test_meid_in_credentials_v1_rds():
    db_instance_id = "belu-metadata-database-1-instance-1"
    region = "us-east-1"

    meid = jmes_custom_functions._func_dt_meid_rds_v1(db_instance_id, region)
    assert meid == "RELATIONAL_DATABASE_SERVICE-D7231D65F633F25E"

def test_meid_in_credentials_v1_s3():
    input = "asdf-faileddatabucket-1hmjl4gib4y81"
    real_meid_from_dt_cluster="S3BUCKET-3AB249FB375BF90D"

    meid = jmes_custom_functions._func_dt_meid_s3_bucket_v1(input)
    assert meid == real_meid_from_dt_cluster

def test_meid_in_credentials_v1_supporting_service():
    supporting_service_name="api gateway"
    region="us-east-1"
    main_dimension="ApiName"
    name="9s5z5yc4hg"

    # meid = jmes_custom_functions._func_dt_meid_supporting_service_v1(supporting_service_name, region, main_dimension, name)
    # assert meid == "CUSTOM_DEVICE-050ED2C3D524BD09"
    # uncomment on implemented

def test_meid_in_credentials_v1_supporting_service_kinesis():
    supporting_service_name="firehose"
    region="us-east-1"
    main_dimension="DeliveryStreamName"
    name="metricstreamsclientintegrationtest-1623184015-65467-00xJBhS9aZoO"
    # input = 'firehose-us-east-1-DeliveryStreamName-metricstreamsclientintegrationtest-1623184015-65467-00xJBhS9aZoO'

    # meid = jmes_custom_functions._func_dt_meid_supporting_service_v1(supporting_service_name, region, main_dimension, name)
    # assert meid == "CUSTOM_DEVICE-0FC9B94D91F488A6"
    # uncomment on implemented
