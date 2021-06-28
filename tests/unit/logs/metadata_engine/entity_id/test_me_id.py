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



def test_meid_credentials_v1_legacy_md5():
    input = "dynatrace-aws-logs-Lambda-1K7HG2Q2LIQKUus-east-1_000047316593"

    id = me_id._legacy_entity_id_md5(input)
    meid = me_id.meid_md5("AWS_LAMBDA_FUNCTION", input)
    meid_from_list = me_id.meid_md5("AWS_LAMBDA_FUNCTION", "dynatrace-aws-logs-Lambda-1K7HG2Q2LIQKU", "us-east-1_000047316593")

    assert id == -3464187019831048966
    assert meid == "AWS_LAMBDA_FUNCTION-CFECBC426F7384FA"
    assert meid == meid_from_list

def test_meid_credentials_v2_supporting_service__murmurhash():
    input = "api gatewayarn:aws:apigateway:us-east-1:000047316593:/restapis/PetStore"

    id = me_id._murmurhash2_64A(input)
    meid = me_id.meid_murmurhash("CUSTOM_DEVICE", input)
    meid_from_list = me_id.meid_murmurhash("CUSTOM_DEVICE", "api gateway", "arn:aws:apigateway:us-east-1:000047316593:/restapis/PetStore")

    assert id == -364647979568170292
    assert meid == "CUSTOM_DEVICE-FAF0829835C67ACC"
    assert meid == meid_from_list

def test_meid_in_credentials_v2_core_services__murmurhash_awsseed():
    real_long_id_from_dt_cluster = 7316649878848848536
    real_meid_from_dt_cluster = "RELATIONAL_DATABASE_SERVICE-6589F64CAEB0C298"

    wrong_default_long_id = 5481040344698372608
    wrong_default_meid = "RELATIONAL_DATABASE_SERVICE-4C1091275954C200"

    dbInstanceArn = "arn:aws:rds:us-east-1:908047316593:db:belu-metadata-database-1-instance-1"
    entity_type = "RELATIONAL_DATABASE_SERVICE"

    id = me_id._murmurhash2_64A(dbInstanceArn)
    meid = me_id.meid_murmurhash(entity_type, dbInstanceArn)
    assert meid == wrong_default_meid, "From default calculation, with seed unset/default (0xe17a1465): 3782874213:"
    assert id == wrong_default_long_id

    id = me_id._murmurhash2_64A(dbInstanceArn, seed=3782874213)
    meid = me_id.meid_murmurhash(entity_type, dbInstanceArn)
    assert meid == wrong_default_meid, "From default calculation, with seed given explicitly, same as default (0xe17a1465): 3782874213:"
    assert id == wrong_default_long_id

    id = me_id._murmurhash2_64A(dbInstanceArn, seed=-512093083)
    meid = me_id.meid_murmurhash_awsseed(entity_type, dbInstanceArn)
    assert meid == real_meid_from_dt_cluster, "From awsSeed calculation, with seed -512093083:"
    assert id == real_long_id_from_dt_cluster

    jmes_custom_functions = jmespath.MappingCustomFunctions()
    meid = jmes_custom_functions._func_dt_meid_rds_v2(dbInstanceArn)
    assert meid == real_meid_from_dt_cluster, "From jmesPath customFunctions - seed should be -512093083:"
    assert id == real_long_id_from_dt_cluster
