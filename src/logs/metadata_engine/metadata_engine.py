# pylint: skip-file
import json
import os
import re
from dataclasses import dataclass
from os import listdir
from os.path import isfile
from typing import Dict, List, Optional, Any
from pygrok import Grok

import jmespath

from util import logging
from .jmespath import JMESPATH_OPTIONS


_CONDITION_COMPARATOR_MAP = {
    "$eq".casefold(): lambda x, y: str(x).casefold() == str(y).casefold(),
    "$prefix".casefold(): lambda x, y: str(x).casefold().startswith(str(y).casefold()),
    "$contains".casefold(): lambda x, y: str(y).casefold() in str(x).casefold(),
}

_SOURCE_VALUE_EXTRACTOR_MAP = {
    "log_group".casefold(): lambda record, parsed_record: record.get("log_group", ""),
}


@dataclass(frozen=True)
class Attribute:
    key: str
    pattern: str


class SourceMatcher:
    source: str
    condition: str
    valid = True

    _evaluator = None
    _operand = None
    _source_value_extractor = None

    def __init__(self, source: str, condition: str):
        self.source = source
        self.condition = condition
        for key in _CONDITION_COMPARATOR_MAP.keys():
            if condition.startswith(key):
                self._evaluator = _CONDITION_COMPARATOR_MAP[key]
                break
        operands = re.findall(r"'(.*?)'", condition, re.DOTALL)
        self._operand = operands[0] if operands else None
        self._source_value_extractor = _SOURCE_VALUE_EXTRACTOR_MAP.get(source.casefold(), None)

        if not self._source_value_extractor:
            logging.warning(f"Unsupported source type: '{source}'")
            self.valid = False
        if not self._evaluator or not self._operand:
            logging.warning(f"Failed to parse condition macro for expression: '{condition}'")
            self.valid = False

    def match(self, record: Dict, parsed_record: Dict) -> bool:
        value = self._extract_value(record, parsed_record)
        return self._evaluator(value, self._operand)

    def _extract_value(self, record: Dict, parsed_record: Dict) -> Any:
        return self._source_value_extractor(record, parsed_record)


@dataclass(frozen=True)
class ConfigRule:
    entity_type_name: str
    source_matchers: List[SourceMatcher]
    attributes: List[Attribute]
    aws_loggroup_pattern: Optional[str]


class MetadataEngine:
    rules: List[ConfigRule]
    default_rule: ConfigRule = None

    def __init__(self):
        self.rules = []
        self._load_configs()

    def _load_configs(self):
        working_directory = os.path.dirname(os.path.realpath(__file__))
        config_directory = os.path.join(working_directory, "../..", "config")
        config_files = [
            file for file
            in listdir(config_directory)
            if isfile(os.path.join(config_directory, file)) and _is_json_file(file)
        ]
        for file in config_files:
            config_file_path = os.path.join(config_directory, file)
            try:
                with open(config_file_path) as config_file:
                    config_json = json.load(config_file)
                    if config_json.get("name", "") == "default":
                        self.default_rule = _create_config_rules(config_json)[0]
                    else:
                        self.rules.extend(_create_config_rules(config_json))
            except Exception:
                logging.exception(f"Failed to load configuration file: '{config_file_path}'")

    def apply(self, record: Dict, parsed_record: Dict):
        try:
            for rule in self.rules:
                if _check_if_rule_applies(rule, record, parsed_record):
                    _apply_rule(rule, record, parsed_record)
                    return
            # No matching rule has been found, applying the default rule
            if self.default_rule:
                _apply_rule(self.default_rule, record, parsed_record)
        except Exception:
            logging.exception(f"Encountered exception when running Rule Engine")


def _check_if_rule_applies(rule: ConfigRule, record: Dict, parsed_record: Dict):
    return all([matcher.match(record, parsed_record) for matcher in rule.source_matchers])


def _apply_rule(rule, record, parsed_record):
    if rule.aws_loggroup_pattern and "log_group" in record:
        extracted_values = parse_aws_loggroup_with_grok_pattern(record["log_group"], rule.aws_loggroup_pattern)
        record.update(extracted_values)

    for attribute in rule.attributes:
        try:
            value = jmespath.search(attribute.pattern, record, JMESPATH_OPTIONS)
            if value:
                parsed_record[attribute.key] = value
        except Exception:
            logging.exception(f"Encountered exception when evaluating attribute {attribute} of rule for {rule.entity_type_name}")

grok_by_pattern = {}

def get_grok(pattern):
    grok = grok_by_pattern.get(pattern, None)
    if grok == None:
        grok = Grok(pattern)
        grok_by_pattern[pattern] = grok
    return grok


def parse_aws_loggroup_with_grok_pattern(loggroup, pattern) -> dict:
    grok = get_grok(pattern)
    extracted_values = grok.match(loggroup)

    if not extracted_values:
        logging.exception(f"Failed to match logGroup '{loggroup}' against the pattern '{pattern}'")
        return {}

    return extracted_values


def _create_sources(sources_json: List[Dict]) -> List[SourceMatcher]:
    result = []

    for source_json in sources_json:
        source = source_json.get("source", None)
        condition = source_json.get("condition", None)
        source_matcher = None

        if source and condition:
            source_matcher = SourceMatcher(source, condition)

        if source_matcher and source_matcher.valid:
            result.append(source_matcher)
        else:
            logging.warning(f"Encountered invalid rule source, parameters were: source= {source}, condition = {condition}")
            return []

    return result


def _create_attributes(attributes_json: List[Dict]) -> List[Attribute]:
    result = []

    for source_json in attributes_json:
        key = source_json.get("key", None)
        pattern = source_json.get("pattern", None)

        if key and pattern:
            result.append(Attribute(key, pattern))
        else:
            logging.warning(f"Encountered invalid rule attribute with missing parameter, parameters were: key = {key}, pattern = {pattern}")

    return result


def _create_config_rule(entity_name: str, rule_json: Dict) -> Optional[ConfigRule]:
    sources_json = rule_json.get("sources", [])
    if entity_name != "default" and not sources_json:
        logging.warning(f"Encountered invalid rule with missing sources for config entry named {entity_name}")
        return None
    sources = _create_sources(sources_json)
    if entity_name != "default" and not sources:
        logging.warning(f"Encountered invalid rule with invalid sources for config entry named {entity_name}: {sources_json}")
        return None
    attributes = _create_attributes(rule_json.get("attributes", []))

    try:
        aws_loggroup_pattern = rule_json["aws"]["logGroup"]
    except KeyError:
        aws_loggroup_pattern = None

    return ConfigRule(entity_type_name=entity_name, source_matchers=sources, attributes=attributes,
                      aws_loggroup_pattern=aws_loggroup_pattern)


def _create_config_rules(config_json: Dict) -> List[ConfigRule]:
    name = config_json.get("name", "")
    created_rules = [_create_config_rule(name, rule_json) for rule_json in config_json.get("rules", [])]
    return [created_rule for created_rule in created_rules if created_rule is not None]


def _is_json_file(file: str) -> bool:
    return file.endswith(".json")