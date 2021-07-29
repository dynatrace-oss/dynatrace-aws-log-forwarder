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
from unittest.mock import patch

import pytest

from logs.metadata_engine import metadata_engine
from logs.metadata_engine.metadata_engine import MetadataEngine


@pytest.mark.parametrize("testcase", [

    ({
        "log_group": 'API-Gateway-Execution-Logs_8zcb3dxf4l/DEV',
        "pattern": 'API-Gateway-Execution-Logs_%{DATA:api_id}/%{GREEDYDATA:stage_name}',
        "parse_output": {
            "api_id": "8zcb3dxf4l",
            "stage_name": "DEV",
        },
    }),

    ({
        "log_group": '/aws/lambda/marek-lambda',
        "pattern": '/aws/lambda/%{GREEDYDATA:function_name}',
        "parse_output": {
            "function_name": "marek-lambda",
        },
    }),

])
def test_parse_aws_loggroup_with_grok_pattern(testcase):
    actual_output = metadata_engine.parse_aws_loggroup_with_grok_pattern(testcase["log_group"], testcase["pattern"])

    assert actual_output == testcase["parse_output"]


def test_default_match():
    non_matching_input = {"logGroup": "SOMETHING_NOT_RECOGNIZED"}
    output = run_with_clean_engine(non_matching_input)

    assert "aws.service" not in output


def run_with_clean_engine(input):
    engine = metadata_engine.MetadataEngine()
    output = {}
    engine.apply(input, output)
    return output
