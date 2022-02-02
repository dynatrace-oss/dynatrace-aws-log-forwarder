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

import json
import time

import pytest

import logs.main
import logs.transformation
from logs.models.batch_metadata import BatchMetadata
from util.context import Context

BATCH_METADATA = BatchMetadata("444000444", "us-east-1", "aws")
CONTEXT = Context("function-name", "dt-url", "dt-token", False, False, "log.forwarder")

CLOUDTRAIL_USER_IDENTITY = {
    "type": "AssumedRole",
    "principalId": "AIDA12345667789ABCEF:444000444-somemonitoringuser",
    "arn": "arn:aws:iam::444000444:user/somemonitoringuser",
    "accountId": "444000444",
    "accessKeyId": "AKIA123456789ABCDEFG",
    "sessionContext": {
        "sessionIssuer": {
            "type": "Role",
            "principalId": "AIDA12345667789ABCEF",
            "arn": "arn:aws:iam::444000444:role/sso/dtRoleAdmin",
            "accountId": "444000444",
            "userName": "dtRoleAdmin"
        },
        "webIdFederationData": {},
        "attributes": {
            "mfaAuthenticated": "false",
            "creationDate": "2021-06-21T06:30:44Z"
        }
    }
}

@pytest.mark.parametrize("testcase", [

    pytest.param({
        "record_data_decoded": {
            "logGroup": "/aws/rds/cluster/aurora-mysql/general",
            "logStream": "aurora-mysql-instance-1",
            "messageType": "DATA_MESSAGE",
            "owner": "444000444",
            "subscriptionFilters": ["mysql-audit-filter"],
            "logEvents": [
                {
                    "id": "35958590510527767165636549608812769529777864588249006080",
                    "timestamp": "12345",
                    "message": "2021-08-10T09:57:26.077268Z    2 Query	SELECT durable_lsn, current_read_point, server_id, last_update_timestamp FROM information_schema.replica_host_status;"
                }
            ],
        },
        "expect_first_log_contains": {
            "aws.service": "rds",
            "aws.resource.id": "aurora-mysql",
            "aws.arn": "arn:aws:rds:us-east-1:444000444:db:aurora-mysql-instance-1",
            "dt.source_entity": "RELATIONAL_DATABASE_SERVICE-FC361C8F808383AE",
            'content': "2021-08-10T09:57:26.077268Z    2 Query	SELECT durable_lsn, current_read_point, server_id, last_update_timestamp FROM information_schema.replica_host_status;",
            'cloud.provider': 'aws',
            'cloud.account.id': "444000444",
            'cloud.region': "us-east-1",
            'aws.log_group': "/aws/rds/cluster/aurora-mysql/general",
            'aws.log_stream': "aurora-mysql-instance-1",
            'aws.region': "us-east-1",
            'aws.account.id': "444000444",
            'severity': 'INFO',
            'log.source': 'rds - general logs',
        },
        "perf_check": {
            "repeat_record": 10000,
            "time_limit_sec": 5
            # roughly 1,5MB of content, ~7MB counting whole log entry with metadata
        }
    }, id="testcase_rds_aurora_mysql_general_log")

])
def test_full_transformation(testcase: dict):
    record_data_decoded = testcase["record_data_decoded"]
    expect_first_log_contains = testcase["expect_first_log_contains"]

    logs_sent = []

    if "perf_check" in testcase:
        perf_check = testcase["perf_check"]
        repeat_record = perf_check["repeat_record"]
        time_limit_sec = perf_check["time_limit_sec"]
    else:
        repeat_record = 1
        time_limit_sec = None

    start_sec = time.time()
    for i in range(repeat_record):
        logs_sent = logs.transformation.extract_dt_logs_from_single_record(
            json.dumps(record_data_decoded), BATCH_METADATA, CONTEXT)
    end_sec = time.time()

    if time_limit_sec:
        duration_sec = end_sec - start_sec
        print(f"PERF_CHECK {duration_sec}")
        assert duration_sec < time_limit_sec, f"Perf check: duration ({duration_sec}s) should be less than limit {time_limit_sec}s"

    assert len(logs_sent) == len(record_data_decoded["logEvents"])

    first_log = logs_sent[0]

    for k, expected_value in expect_first_log_contains.items():
        if expected_value == None:
            assert k not in first_log, f"key={k} not expected in the output, actual={first_log[k]}"
        else:
            assert first_log.get(k,
                                 None) == expected_value, f"key={k}, expected value={expected_value}, actual={first_log.get(k, None)}"
