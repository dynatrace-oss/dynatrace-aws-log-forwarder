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

from unittest import TestCase
from logs import input_records_decoder


class Test(TestCase):

    def test_check_records_list_if_logs_end_decode(self):
        records = [
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
        ]

        is_logs, decoded_records = input_records_decoder.check_records_list_if_logs_end_decode(records)

        self.assertTrue(is_logs)

        expected_first = r'{"messageType":"DATA_MESSAGE","owner":"444652832050","logGroup":"cloudwatch_customlog","logStream":"2021-02-04-logstream","subscriptionFilters":["b-SubscriptionFilter0-1I0DE5MAAFV5G"],"logEvents":[{"id":"35958590510527767165636549608812769529777864588249006080","timestamp":1612438965174,"message":"2021-02-04 12:42:47\tlog message"}]}'
        expected_second = r'{"messageType":"DATA_MESSAGE","owner":"444652832050","logGroup":"cloudwatch_customlog","logStream":"2021-02-04-logstream","subscriptionFilters":["b-SubscriptionFilter0-1I0DE5MAAFV5G"],"logEvents":[{"id":"35958591301289891160333915627296360039224104084779368448","timestamp":1612439000633,"message":"2021-02-04 12:43:22\tlog message"}]}'

        self.assertEqual(decoded_records[0], expected_first)
        self.assertEqual(decoded_records[1], expected_second)

    def test_check_records_list_if_logs_end_decode_not_logs(self):
        records = [
            {
                "ZGRkCg==": "49615192443673540283798383997441439122248557324429950978000000",
                "approximateArrivalTimestamp": 1612438967376,
                "data": "ZGRkCg=="
            },
        ]

        is_logs, decoded_records = input_records_decoder.check_records_list_if_logs_end_decode(records)

        self.assertFalse(is_logs)
