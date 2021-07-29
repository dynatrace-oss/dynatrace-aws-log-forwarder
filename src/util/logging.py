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

import traceback
from typing import Text

from util.context import Context


def log_multiline_message(message: Text):
    # need to modify endline char to have multiline log record not split into multiple log entries in CloudWatch:
    message = message.replace('\n', ' ')
    print(message)


def debug_log_multiline_message(message: Text, context: Context):
    if context.debug:
        log_multiline_message("DEBUG: " + message)


def log_error_with_stacktrace(e: Exception, msg):
    log_multiline_message(f"Exception '{e}' occurred. Additional message: '{msg}'")
    log_multiline_message(traceback.format_exc())

def log_error_without_stacktrace(msg):
    log_multiline_message(msg + "Exception details: " + traceback.format_exc(limit=0))


# wrappers for metadata_engine (there is different logging approach there):

def exception(msg):
    log_multiline_message(msg + "Exception details: " + traceback.format_exc())

def warning(msg):
    log_multiline_message("WARNING: " + msg)
