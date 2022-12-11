import json
import os
import re

class MissingMessageException(Exception):
    pass
class TypeNotDefinedInMappingException(Exception):
    pass

class MappingProcessor:
    def __init__(self, mapping_filename="mqtt_message_mapping.json"):
        self._load_file(mapping_filename)
        self._process_mapping()

    def _process_mapping(self):
        self.mqtt_topic = self._raw_mapping["mqtt_subtopic"]
        self.measurement = self._raw_mapping["measurement"]
        self.name = self._raw_mapping["name"]
        self.regex = self._raw_mapping["regex"]
        self.regex_mapping = self._raw_mapping["regex_mapping"]
        self.mqtt_to_influx = {item["type"]: InfluxMapping(item) for item in self._raw_mapping["mqtt_to_influx"]}
        self.topics = set(self.mqtt_to_influx.keys())

    def _load_file(self, filename="mqtt_message_mapping.json"):
        with open(filename, "r") as f:
            self._raw_mapping = json.load(f)

    def to_influx_json(self, message, topic):
        regex_result = self._process_regex(topic)
        if message is None or topic is None:
            raise MissingMessageException("missing message!")
        influx_object = {
            "measurement": self.measurement,
            "tags": self._get_tags(regex_result),
            "fields": self._get_fields(message, regex_result),
            "time": message["Time"]
        }
        return influx_object

    def _get_tags(self, regex_result):
        tags = {
            "name": self.name
        }
        for key, val in self.regex_mapping.items():
            tags.update({key: regex_result[0][val].replace("_", "")})
        return tags

    def _process_regex(self, topic):
        r = re.compile(self.regex)
        regex_result = r.findall(topic)
        return regex_result

    def _get_fields(self, message, regex_result):
        if "type" not in self.regex_mapping:
            raise TypeNotDefinedInMappingException
        type_id = self.regex_mapping["type"]
        im_variant = regex_result[0][type_id]
        im = self.mqtt_to_influx[im_variant]
        fields = im.get_fields(message)
        return fields

class InfluxMapping:
    def __init__(self, raw):
        self.name = raw["name"]
        self.mqtt_topic_type = raw["type"]
        self.influx_mapping = raw["influx_mapping"]

    def get_fields(self, message:dict={}):
        fields = {}
        for field in self.influx_mapping:
            if isinstance(field, list):
                pass
            elif isinstance(field, dict):
                n = field["name"]
                path = [n]
                items = field["items"]
                hide_prefix = field["hide_prefix"]
                fields.update(self._resolve_nested(path, items, message, hide_prefix))
            else:
                fields[field] = message[field]
        return fields

    def _resolve_nested(self, path, items, message, hide_prefix=False):
        m = message
        name = ""
        for p in path:
            m = m[p]
            name += p
        result = {}
        for i in items:
            item_name = i
            if not hide_prefix:
                item_name = name + item_name
            result[item_name] = m[i]
        return result

