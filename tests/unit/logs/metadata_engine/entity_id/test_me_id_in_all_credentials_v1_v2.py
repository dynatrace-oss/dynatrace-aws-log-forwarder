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

def test_meid_in_all_credentials_lambda__md5():
    functionName="dynatrace-aws-logs-Lambda-1K7HG2Q2LIQKU"
    region="us-east-1"
    accountId = "908047316593"
    real_meid_from_dt_cluster="AWS_LAMBDA_FUNCTION-38D1027DFA41ADD1"

    jmes_custom_functions = jmespath.MappingCustomFunctions()
    meid = jmes_custom_functions._func_dt_meid_lambda_function(functionName, region, accountId)
    assert meid == real_meid_from_dt_cluster

def test_meid_in_all_credentials_ec2_instance():
    instance_id = "i-0a6453b0c36d4b9c0"
    real_meid_from_dt_cluster="EC2_INSTANCE-9D980F5F75A71C04"

    jmes_custom_functions = jmespath.MappingCustomFunctions()
    meid = jmes_custom_functions._func_dt_meid_ec2_instance(instance_id)
    assert meid == real_meid_from_dt_cluster

def test_meid_in_all_credentials_ebs_volume():
    volume_id = "vol-0fbeb9deba719a00d"
    real_meid_from_dt_cluster="EBS_VOLUME-F8559CCFC08C8AAD"

    jmes_custom_functions = jmespath.MappingCustomFunctions()
    meid = jmes_custom_functions._func_dt_meid_ebs_volume(volume_id)
    assert meid == real_meid_from_dt_cluster