import pytest
from .mapping_processor import MappingProcessor
import json


expected_result1 = json.loads("""
{
  "measurement": "powerplugs",
  "tags": {
    "name": "GosundSP1",
    "device": "waschmaschine",
    "type": "SENSOR"
  },
  "fields": {
    "ApparentPower": 0,
    "Current": 0.0,
    "Factor": 0.0,
    "Period": 0,
    "Power": 0,
    "ReactivePower": 0,
    "Today": 0.0,
    "Total": 11.242,
    "TotalStartTime": "2022-09-09T12:32:17",
    "Voltage": 210,
    "Yesterday": 0.0
  },
  "time": "2022-12-10T18:53:13"
}
""")

expected_result2 = json.loads("""
{
  "measurement": "powerplugs",
  "tags": {
    "name": "GosundSP1",
    "device": "waschmaschine",
    "type": "STATE"
  },
  "fields": {
    "UptimeSec": 4492793,
    "Heap": 25,
    "Sleep": 50,
    "LoadAvg": 19,
    "MqttCount": 59,
    "POWER": "ON",
    "WifiChannel": 5,
    "WifiMode": "11n",
    "WifiRSSI": 54,
    "WifiSignal": -73,
    "WifiLinkCount": 9,
    "WifiDowntime": "0T00:49:06"
  },
  "time": "2022-12-10T18:53:13"
}
""")



def test_mapping_processor_sensor():
    mp = MappingProcessor("test_mqtt_message_mapping.json")
    o = {
        "topic": "power_plugs/tele/waschmaschine/SENSOR",
        "message": '{"Time":"2022-12-10T18:53:13","ENERGY":{"TotalStartTime":"2022-09-09T12:32:17","Total":11.242,"Yesterday":0.000,"Today":0.000,"Period": 0,"Power": 0,"ApparentPower": 0,"ReactivePower": 0,"Factor":0.00,"Voltage":210,"Current":0.000}}'
    }
    message = json.loads(o["message"])
    influx_json = mp.to_influx_json(message, o["topic"])
    assert influx_json == expected_result1


def test_mapping_processor_state():
    mp = MappingProcessor("test_mqtt_message_mapping.json")
    o = {
        "topic": "power_plugs/tele/waschmaschine/STATE",
        "message": '{"Time":"2022-12-10T18:53:13","Uptime":"51T23:59:53","UptimeSec":4492793,"Heap":25,"SleepMode":"Dynamic","Sleep":50,"LoadAvg":19,"MqttCount":59,"POWER":"ON","Wifi":{"AP":1,"SSId":"Gorgonzola","BSSId":"E8:DF:70:CD:5A:00","Channel":5,"Mode":"11n","RSSI":54,"Signal":-73,"LinkCount":9,"Downtime":"0T00:49:06"}}'
    }
    message = json.loads(o["message"])
    influx_json = mp.to_influx_json(message, o["topic"])
    assert influx_json == expected_result2
