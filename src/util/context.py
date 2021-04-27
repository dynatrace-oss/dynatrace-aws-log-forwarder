from typing import Text


class Context:
    def __init__(self, function_name: Text, dt_url: str, dt_token: str, debug: bool, verify_SSL: bool):
        self.function_name: Text = function_name
        self.dt_url = dt_url
        self.dt_token = dt_token
        self.debug: bool = debug
        self.verify_SSL: bool = verify_SSL
