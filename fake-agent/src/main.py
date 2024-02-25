from paho.mqtt import client as mqtt_client
import time
from schema.aggregated_data_schema import AggregatedDataSchema
from file_datasource import FileDatasource
from utils.infinite_repetitive_range import InfiniteRepetitiveRange
import config


def connect_mqtt(broker, port):
    """Create MQTT client"""
    print(f"CONNECT TO {broker}:{port}")

    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print(f"Connected to MQTT Broker ({broker}:{port})!")
        else:
            print("Failed to connect {broker}:{port}, return code %d\n", rc)
            exit(rc)

    client = mqtt_client.Client()
    client.on_connect = on_connect
    client.connect(broker, port)
    client.loop_start()
    return client


def publish(client, topic, datasource, delay):
    accel, gps, parking = datasource.startReading()
    agr_data = datasource.read(accel, gps, parking)
    datasource.stopReading(accel, gps, parking)

    for count in InfiniteRepetitiveRange.infinite_repetitive_range(len(agr_data)):
        time.sleep(delay)
        msg = AggregatedDataSchema().dumps(agr_data[count])
        result = client.publish(topic, msg)

        status = result[0]

        if status == 0:
            print(f"Send `{msg}` to topic `{topic}`")
        else:
            print(f"Failed to send message to topic {topic}")


def run():
    client = connect_mqtt(config.MQTT_BROKER_HOST, config.MQTT_BROKER_PORT)
    datasource = FileDatasource(
        "data/accelerometer.csv", "data/gps.csv", "data/parking.csv"
    )
    publish(client, config.MQTT_TOPIC, datasource, config.DELAY)


if __name__ == "__main__":
    run()
