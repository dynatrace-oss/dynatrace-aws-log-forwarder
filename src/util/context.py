#     Copyright 2021 Dynatrace LLC
#
#     Licensed under the Apache License, Version 2.0 (the "License");
#     you may not use this file except in compliance with the License.
#     You may obtain a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#     Unless required by applicable law or agreed to in writing, software
#     distributed under the License is distributed on an "AS IS" BASIS,
#     WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#     See the License for the specific language governing permissions and
#     limitations under the License.

from typing import Text

from logs.self_monitoring.sfm import SelfMonitoringContext


class Context:
    def __init__(self, function_name: Text, dt_url: str, dt_token: str, debug: bool, verify_SSL: bool):
        self.function_name: Text = function_name
        self.dt_url = dt_url
        self.dt_token = dt_token
        self.debug: bool = debug
        self.verify_SSL: bool = verify_SSL
        self.sfm = SelfMonitoringContext(function_name)
