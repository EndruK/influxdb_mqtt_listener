import paho.mqtt.client as mqtt
from influxdb_client import InfluxDBClient
from influxdb_client.client.write_api import SYNCHRONOUS
import json
from json import JSONDecodeError
from mapping_processor import MappingProcessor
from dotenv import load_dotenv
import os
import logging

load_dotenv()

INFLUXDB_ADDRESS = os.getenv("INFLUXDB_ADDRESS", "http://localhost:8086")
INFLUXDB_ORG = os.getenv("INFLUXDB_ORG")
INFLUXDB_TOKEN = os.getenv("INFLUXDB_TOKEN")
INFLUXDB_BUCKET = os.getenv("INFLUXDB_BUCKET")

MQTT_ADDRESS = os.getenv(("MQTT_ADDRESS"), "localhost")
MQTT_PORT = int(os.getenv("MQTT_PORT", 1883))
MQTT_USER = os.getenv("MQTT_USER")
MQTT_PASSWORD = os.getenv("MQTT_PASSWORD")
MQTT_TOPIC = os.getenv("MQTT_TOPIC")
MQTT_CLIENT_ID = os.getenv("MQTT_CLIENT_ID", "PythonMQTTListener")

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

influx_debug = False
if LOG_LEVEL == "DEBUG":
    influx_debug = True

influxdb_client = InfluxDBClient(
    url=INFLUXDB_ADDRESS,
    token=INFLUXDB_TOKEN,
    org=INFLUXDB_ORG,
    debug=influx_debug
)
write_api = influxdb_client.write_api(write_options=SYNCHRONOUS)


def on_connect(client, userdata, flags, rc):
    logging.info(f"connected! {str(rc)}")
    client.subscribe(MQTT_TOPIC)

def on_message(client, userdata, msg):
    logging.debug(f"{msg.topic} {str(msg.payload)}")
    decoded_msg = msg.payload.decode("utf-8")
    topic = msg.topic
    try:
        message = json.loads(decoded_msg)
        mp = MappingProcessor()
        subtopic = topic.split("/")[-1]
        if  subtopic in mp.topics:
            result = mp = mp.to_influx_json(message, topic)
            logging.debug(json.dumps(result, indent=2))
            response = write_api.write(bucket=INFLUXDB_BUCKET, record=result)
    except JSONDecodeError:
        logging.warning(f"can't process json: {topic} : {decoded_msg}")

def main():
    
    logging.basicConfig(level=logging.getLevelName(LOG_LEVEL))
    logging.info(f"set log level to {LOG_LEVEL}")

    mqttc = mqtt.Client()
    mqttc.username_pw_set(MQTT_USER, MQTT_PASSWORD)
    mqttc.on_connect = on_connect
    mqttc.on_message = on_message

    mqttc.connect(MQTT_ADDRESS, MQTT_PORT)
    mqttc.loop_forever()

if __name__ == "__main__":
    main()