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

LOG_THROTTLING_LIMIT_PER_CALLER = 10

log_call_count = dict()


def log_multiline_message(message: Text, caller: Text):

    # display logs called from one spot no more than the specified amount of times
    if log_call_count.get(caller, 0) < LOG_THROTTLING_LIMIT_PER_CALLER:
        log_call_count[caller] = log_call_count.get(caller, 0) + 1
    elif log_call_count.get(caller, 0) == LOG_THROTTLING_LIMIT_PER_CALLER:
        log_call_count[caller] = log_call_count.get(caller, 0) + 1
        print(f"Logging calls from caller '{caller}' exceeded the throttling limit of",
              f"{LOG_THROTTLING_LIMIT_PER_CALLER}. Further logs from this caller will be discarded")
        return
    else:
        return

    # need to modify endline char to have multiline log record not split into multiple log entries in CloudWatch:
    message = message.replace('\n', ' ')
    print(message)


def debug_log_multiline_message(message: Text, context: Context, caller: Text):
    if context.debug:
        log_multiline_message("DEBUG: " + message, caller)


def log_error_with_stacktrace(e: Exception, msg, caller: Text):
    log_multiline_message(f"Exception '{e}' occurred. Additional message: '{msg}' " + traceback.format_exc(), caller)


def log_error_without_stacktrace(msg, caller: Text):
    log_multiline_message(msg + "Exception details: " + traceback.format_exc(limit=0), caller)


# wrappers for metadata_engine (there is different logging approach there):

def exception(msg, caller):
    log_multiline_message(msg + "Exception details: " + traceback.format_exc(), caller)


def warning(msg, caller):
    log_multiline_message("WARNING: " + msg, caller)
