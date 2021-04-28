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


# wrappers for metadata_engine (there is different logging approach there):

def exception(msg):
    log_multiline_message("EXCEPTION: " + msg)


def warning(msg):
    log_multiline_message("WARNING: " + msg)
