from logs.metadata_engine import me_id


def test_meid_murmurhash():
    input = "api gatewayarn:aws:apigateway:us-east-1:000047316593:/restapis/PetStore"

    id = me_id._murmurhash2_64A(input)
    meid = me_id.meid_murmurhash("CUSTOM_DEVICE", input)

    assert id == -364647979568170292
    assert meid == "CUSTOM_DEVICE-FAF0829835C67ACC"


def test_meid_md5():
    input = "dynatrace-aws-logs-Lambda-1K7HG2Q2LIQKUus-east-1_000047316593"

    id = me_id._legacy_entity_id_md5(input)
    meid = me_id.meid_md5("AWS_LAMBDA_FUNCTION", input)

    assert id == -3464187019831048966
    assert meid == "AWS_LAMBDA_FUNCTION-CFECBC426F7384FA"
