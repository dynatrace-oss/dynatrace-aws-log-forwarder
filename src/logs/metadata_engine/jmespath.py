# pylint: skip-file
import re

import jmespath
from jmespath import functions

from logs.metadata_engine import me_id


class MappingCustomFunctions(functions.Functions):

    @functions.signature({'types': ['string']},
                         {'types': ['string']},
                         {'types': ['string']})
    def _func_replace_regex(self, subject, regex, replacement):
        # replace java capture group sign ($) to python one (\)
        processed_replacement = re.sub(r'\$(\d+)+', '\\\\\\1', replacement)
        compiled_regex = re.compile(regex)
        result = compiled_regex.sub(processed_replacement, subject)
        return result

    @functions.signature({'types': []},
                         {'types': ['expref']},
                         {'types': ['expref']},
                         {'types': []})
    def _func_if(self, condition, if_true_expression, if_false_expression, node_scope):
        if condition:
            return if_true_expression.visit(if_true_expression.expression, node_scope)
        else:
            return if_false_expression.visit(if_false_expression.expression, node_scope)

    @functions.signature({"types": ['string']},
                         {"types": ['array-string']})
    def _func_format(self, pattern, values):
        assert pattern.count("{}") == len(values)

        output = pattern

        for value in values:
            output = output.replace("{}", value, 1)

        return output

    @functions.signature({'types': ['string']},
                         {'types': ['string']})
    def _func_dt_meid_md5(self, entity_type, hashing_input):
        return me_id.meid_md5(entity_type, hashing_input)

    @functions.signature({'types': ['string']},
                         {'types': ['string']})
    def _func_dt_meid_murmurhash(self, entity_type, hashing_input):
        return me_id.meid_murmurhash(entity_type, hashing_input)

JMESPATH_OPTIONS = jmespath.Options(custom_functions=MappingCustomFunctions())
