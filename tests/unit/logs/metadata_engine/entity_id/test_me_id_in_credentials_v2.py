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

def test_meid_in_credentials_v2_elb():
    arn = "arn:aws:elasticloadbalancing:us-east-1:478983378254:loadbalancer/a016dbd362e6d4da88e1c38597c3c2ec"
    real_meid_from_dt_cluster="ELASTIC_LOAD_BALANCER-8528390864056438"

    meid = jmes_custom_functions._func_dt_meid_elb_v2(arn)
    assert meid == real_meid_from_dt_cluster

def test_meid_in_credentials_v2_nlb():
    arn = "arn:aws:elasticloadbalancing:us-east-1:908047316593:loadbalancer/net/mawo-lb/15849cc195988fcd"
    real_meid_from_dt_cluster="AWS_NETWORK_LOAD_BALANCER-B13CC87CE333B925"

    meid = jmes_custom_functions._func_dt_meid_nlb_v2(arn)
    assert meid == real_meid_from_dt_cluster

def test_meid_in_credentials_v2_alb():
    arn = "arn:aws:elasticloadbalancing:us-east-1:908047316593:loadbalancer/app/awseb-AWSEB-1PVCR48G91GIH/9468cad8f10dd41f"
    real_meid_from_dt_cluster="AWS_APPLICATION_LOAD_BALANCER-E6740856948EA39B"

    meid = jmes_custom_functions._func_dt_meid_alb_v2(arn)
    assert meid == real_meid_from_dt_cluster

def test_meid_in_credentials_v2_auto_scaling_group():
    arn = "arn:aws:autoscaling:us-east-1:908047316593:autoScalingGroup:eae95707-f82d-44c8-ac1a-ab8c0edb73c8:autoScalingGroupName/awseb-e-zyzwkdfndi-stack-AWSEBAutoScalingGroup-RNJ3TG08OKTM"
    real_meid_from_dt_cluster="AUTO_SCALING_GROUP-572DED237D26E608"

    meid = jmes_custom_functions._func_dt_meid_auto_scaling_group_v2(arn)
    assert meid == real_meid_from_dt_cluster

def test_meid_in_credentials_v2_dynamo_db():
    arn = "arn:aws:dynamodb:us-west-1:908047316593:table/METRIC_TEST_2"
    real_meid_from_dt_cluster="DYNAMO_DB_TABLE-C7F2DDDA1E8CC7E0"

    meid = jmes_custom_functions._func_dt_meid_dynamo_db_v2(arn)
    assert meid == real_meid_from_dt_cluster

def test_meid_in_credentials_v2_rds():
    arn = "arn:aws:rds:us-east-1:908047316593:db:belu-metadata-database-1-instance-1"

    meid = jmes_custom_functions._func_dt_meid_rds_v2(arn)
    assert meid == "RELATIONAL_DATABASE_SERVICE-6589F64CAEB0C298"

def test_meid_in_credentials_v2_s3():
    arn = "arn:aws:s3:::asdf-faileddatabucket-1hmjl4gib4y81"
    real_meid_from_dt_cluster="S3BUCKET-E4FC09E997166B4E"

    meid = jmes_custom_functions._func_dt_meid_s3_bucket_v2(arn)
    assert meid == real_meid_from_dt_cluster

def test_meid_in_credentials_v2_supporting_service__murmurhash():
    supporting_service_name = "API Gateway"
    arn = "arn:aws:apigateway:us-east-1:000047316593:/restapis/PetStore"

    meid = jmes_custom_functions._func_dt_meid_supporting_service_v2(supporting_service_name, arn)
    assert meid == "CUSTOM_DEVICE-FAF0829835C67ACC"

def test_meid_in_credentials_v2_supporting_service__murmurhash_api_gateway():
    supporting_service_short_name = "api gateway"
    arn = "arn:aws:apigateway:us-east-1:000047316593:/restapis/PetStore"

    meid = jmes_custom_functions._func_dt_meid_supporting_service_v2(supporting_service_short_name, arn)
    assert meid == "CUSTOM_DEVICE-FAF0829835C67ACC"

