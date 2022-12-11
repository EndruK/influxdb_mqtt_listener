# INFLUXDB and Tasmota Gosund SP1 MQTT listener

## required stuff:
```bash
cd mqtt_listener
cp example.env .env

vim .env
```
- set all required env variables
  - INFLUXDB_ADDRESS = address to influxdb host (http://localhost:8086)
  - INFLUXDB_ORG = influxdb organization of this project
  - INFLUXDB_TOKEN = generated Influxdb API token
  - INFLUXDB_BUCKET = bucket to store measurements ind
  - MQTT_ADDRESS = host of mqtt broker (127.0.0.1)
  - MQTT_PORT = port of mqtt broker (1883)
  - MQTT_USER = username for mqtt auth
  - MQTT_PASSWORD = password for mqtt auth
  - MQTT_TOPIC = subscribe to topic
  - MQTT_CLIENT_ID = identifier of this script for mqtt broker