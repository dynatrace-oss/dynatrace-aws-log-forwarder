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
import os
import pytest
from types import SimpleNamespace
from unittest import mock
from unittest.mock import patch

import index


@mock.patch.dict(
    os.environ, {
        "DYNATRACE_ENV_URL": "https://google.com",
        "DYNATRACE_API_KEY": "token",
        "VERIFY_SSL": "false",
        "DEBUG": "false",
        "LOG_FORWARDER_SETUP_NAME": "log.forwarder"
    })
@pytest.mark.parametrize("testcase", [
    ({
        "lambda_event": {
            "invocationId": "1545b29a-10ca-4f7f-a60f-54195607c98d",
            "deliveryStreamArn": "arn:aws:firehose:us-east-1:444652832050:deliverystream/b-FirehoseLogStreams-lbcTAGyNE8hz",
            "region": "us-east-1",
            "records": [
                {
                    "recordId": "49615192443673540283798383997441439122248557324429950978000000",
                    "approximateArrivalTimestamp": 1612438967376,
                    "data": "H4sIAAAAAAAAAGWQzWrDMBCEXyXobMNK1urHN0Mc00NODr20ITiOSAy2ZSy5oYS8ezcNOZTCnuabZXfmxgYXQnN2u+/JsZyti11x2JZ1XVQlS5i/jm4mWUqpUJhMAALJvT9Xs18mIm3vl9O1ie3l0C4h+oHY01HH2TUDWQQInoJIQaYkh6ecsLAcQzt3U+z8uOn66ObA8g92TOt/AFL+BusSt0WxeceK7X8PlF9ujI+dG+tOdCdDiwYtIAcUWivNFapMobQKjOFCK4vCaq2NkmiMkBaAyCNQ7KiG2AyUiCsuZGasQq5l8qrnT4wVF7mk0Z+R3li9LPf9/Qf9DEk+TwEAAA=="
                },
                {
                    "recordId": "49615192443673540283798383997442648048068174358786342914000000",
                    "approximateArrivalTimestamp": 1612439002747,
                    "data": "H4sIAAAAAAAAAGWQwWrDMBBEfyXobMNqV5Il3wxxTA85OfTShuA4IjXYlrHkhBDy71Ubcii9vpllZufOBut9c7a722RZztbFrjhsy7ouqpIlzF1HO0cshFASNSFIiLh352p2yxSVtnfL6dqE9uvQLj64IWpPRx1m2wzRgoA8BUxBpBH7J06YX46+nbspdG7cdH2ws2f5Bzum9T8BUv4G61Jui2LzLiu2/w0oL3YMPzd31p1iDkkjtTScgKM22nCugIgMlwozNIoUABlEwUGAFllmSGkhdOwSujhDaIb4EVccBRkAUETJa54/b6w45oJyxM8Qa6xelsf+8Q1mxAG9TwEAAA=="
                },
                {
                    "recordId": "49615192443673540283798383997443856973887789262838956034000000",
                    "approximateArrivalTimestamp": 1612439006290,
                    "data": "H4sIAAAAAAAAAGVQy2qDQBT9lTBrhTt37qjjToiRLrIydNOGYMyQCuqIMyaEkH/vbUMWpdvz4DzuYrDeN2e7u01W5GJd7IrDtqzroipFJNx1tDPDRJRozBSCBoZ7d65mt0zMtL1bTtcmtF+HdvHBDcw9FXWYbTOwBAFlDBgDxQz7JxwJvxx9O3dT6Ny46fpgZy/yD3GM638ExPIN1qXeFsXmXVdi/xtQXuwYfjx30Z04R2mjM22kyjgQETOSqVEqNWDQUKpAJkCQIaSJIkk8JQWpJHKX0PENoRl4kUwkkjIA7Mbodc+fGSuJOakck8/ANVYvyWP/+AbSuZ1nTwEAAA=="
                },
                {
                    "recordId": "49615192443673540283798383997445065899707404304330522626000000",
                    "approximateArrivalTimestamp": 1612439011420,
                    "data": "H4sIAAAAAAAAAGWQwWrDMBBEfyXoHMNqpbW8vhnimB5ycuilDcFxRGqwLWPJDSXk36s25FB6fTPLzM5NDNb75mL3X5MVudgU++K4K+u6qEqxFu462jlirXVKmCkEgoh7d6lmt0xRaXu3nK9NaD+O7eKDG6L2cNRhts0QLQgoE8AEdBKxf+C18MvJt3M3hc6N264PdvYifxOnpP4nQCJfYFPSrii2r1SJw29A+WnH8HNzE9055ihiyoilZmAyBhmMylSapaQptjeGiSRKglRpg8ialUJmjF1CF2cIzRA/kqlErRiApcrWz3n+vLGSmGuVK/keYo3V03I/3L8BezNvmk8BAAA="
                }
            ]
        },
        "number_of_logs_expected": 4
    }),
    ({
        "lambda_event": {
            "invocationId": "b7ec4dcd-b374-4997-9253-1fcf69fc7427",
            "deliveryStreamArn": "arn:aws:firehose:us-east-1:908047316593:deliverystream/wojtek-logs-test-FirehoseLogStreams-S0tRv0udxmjx",
            "region": "us-east-1",
            "records": [
                {
                    "recordId": "49617616745552467159839656418319106360158614061332824066000000",
                    "approximateArrivalTimestamp": 1619427317606,
                    "data": "H4sIAAAAAAAAADWOzQqCQBRGX2W4awnsT5pdhLaxggxaRMSkN2dIZ2TuNYno3cOs5eE78J0X1EikSjw8GwQJq932sN+ll02cZct1DAG4zqLvl8q1Rac416krCQKoXLn2rm1AwkAZe1T1gNReKfemYeNsYipGTyBP568XP9Byjy8wxaCzqZFY1Q3IcB4upuNoEkazySL45/UBx1T88sQvT4qVxvxubCk0qoq1cDdRILGxqn8WifGoHeEI3uf3B6pWmIjsAAAA"
                },
                {
                    "recordId": "49617616745552467159839656480374477606797147664149381122000000",
                    "approximateArrivalTimestamp": 1619427368657,
                    "data": "H4sIAAAAAAAAAK1S22rbQBD9FSH6aFV7mb2M3xyshkLdFkvtS2zK2rs2ai3LldZ1k5B/79hJiSEYGujTwpmzey6z92kT+t6tQ3W7C+kwHY+q0bdJUZaj6yIdpO1hGzqCkVkGRnKtUBK8adfXXbvf0SR3hz7fuGbhXX5ov8fwI6Npn60D3XSx7R7pZeyCa4gvmOA5g1zo/ObNh1FVlNVcG7FceOSIKwN8yXAhQQbBlwKcXzJBT/T7Rb/s6l2s2+27ehND16fDm/RcMYY+pvOTWvErbOORcJ/WnkSl5hxAauRMGgsMrLJWArdCaZAKtaEDjOJWK8s4cqUFKm1JONZUUHQNZeWaIwhDfJA4+FscPV9Wo2mVTMPPPVHf+2HiAaVxhmcrvVIZWNAZag2Z8w6ZEN774JOvlIHSDJOnGmbb9GHw0jCAkswwBBBoDIHHBMJKZckhWs6sJfNSGWa5uWgYxLnhY1XJY3cJ1XVJmWphxkrUJMcUIzmhLEeyQw5AoQCDEpXiQsJlZXmuXHwcv7ao/+BO/aO7afH50+s3OYvjPX310y75Ww5J08/iVb3Z0JKfJ+IET0LTdrdJWd8FIgubTK4IdL+Tp8GXPpCqkif8mHz+8AdWQQvHowMAAA=="
                }
            ]
        },
        "number_of_logs_expected": 4 # first record (control message) is ignored, second one has 4 logs
    })
])
def test_full_flow(testcase: dict):
    lambda_event = testcase["lambda_event"]
    number_of_logs_expected = testcase["number_of_logs_expected"]
    lambda_context = SimpleNamespace(function_name="my-function-name")

    client_response = (200, "BODY")

    with patch('util.http_client.perform_http_request_for_json', return_value=client_response) as mock_http_client:
        with patch('boto3.client'):
            response = index.handler(lambda_event, lambda_context)

    # CHECK RESPONSE
    assert len(response["records"]) == len(lambda_event["records"])

    for i, response_record in enumerate(response["records"]):
        input_record = lambda_event["records"][i]
        assert response_record["recordId"] == input_record["recordId"]
        assert response_record["data"], input_record["data"]
        assert response_record["result"], "Ok"

    # CHECK HTTP CALL
    assert mock_http_client.call_count == 1
    request_body_bytes = mock_http_client.call_args[0][1]
    request_body = request_body_bytes.decode('utf-8')
    sent_logs = json.loads(request_body)

    assert len(sent_logs) == number_of_logs_expected

    for log in sent_logs:
        assert log["log.forwarder.setup"] == "log.forwarder"
