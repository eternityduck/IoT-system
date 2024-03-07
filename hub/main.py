import logging
from typing import List
import json

from fastapi import FastAPI
from redis import Redis
import paho.mqtt.client as mqtt

from src.adapters.store_api_adapter import StoreApiAdapter
from src.entities.processed_agent_data import ProcessedAgentData
from config import (
    STORE_API_BASE_URL,
    REDIS_HOST,
    REDIS_PORT,
    BATCH_SIZE,
    MQTT_TOPIC,
    MQTT_BROKER_HOST,
    MQTT_BROKER_PORT,
)


logging.basicConfig(
    level=logging.INFO,  # Set the log level to INFO (you can use logging.DEBUG for more detailed logs)
    format="[%(asctime)s] [%(levelname)s] [%(module)s] %(message)s",
    handlers=[
        logging.StreamHandler(), 
        logging.FileHandler("app.log"), 
    ],
)
    
logging.info("Redis host: %s", REDIS_HOST)
logging.info("Redis port: %s", REDIS_PORT)

redis_client = Redis(host=REDIS_HOST, port=REDIS_PORT)

store_adapter = StoreApiAdapter(api_base_url=STORE_API_BASE_URL)


app = FastAPI()


@app.post("/processed_agent_data/")
async def save_processed_agent_data(processed_agent_data: ProcessedAgentData):
    redis_client.lpush("processed_agent_data", processed_agent_data.model_dump_json())
    if redis_client.llen("processed_agent_data") >= BATCH_SIZE:
        processed_agent_data_batch: List[ProcessedAgentData] = []
        for _ in range(BATCH_SIZE):
            processed_agent_data = ProcessedAgentData.model_validate_json(
                redis_client.lpop("processed_agent_data")
            )
            processed_agent_data_batch.append(processed_agent_data)
        print(processed_agent_data_batch)
        store_adapter.save_data(processed_agent_data_batch=processed_agent_data_batch)
    return {"status": "ok"}


client = mqtt.Client()

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        logging.info("Connected to MQTT broker")
        client.subscribe(MQTT_TOPIC)
    else:
        logging.info(f"Failed to connect to MQTT broker with code: {rc}")


def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode("utf-8"))
        
        model = {
            "road_state": "good",
            "agent_data": {
                "user_id": payload['user_id'],
                "accelerometer": {
                    "x": payload['accelerometer']['x'],
                    "y": payload['accelerometer']['y'],
                    "z": payload['accelerometer']['z']
                },
                "gps": {
                    "latitude": payload['gps']['latitude'],
                    "longitude": payload['gps']['longitude']
                },
                "timestamp": str(payload['timestamp']),
            },
        }

        deserialized = json.dumps(model, default=str)
        
        redis_client.lpush(
            "processed_agent_data", deserialized
        )
        processed_agent_data_batch: List[ProcessedAgentData] = []
        if redis_client.llen("processed_agent_data") >= BATCH_SIZE:
            for _ in range(BATCH_SIZE):
                processed_agent_data = ProcessedAgentData.model_validate_json(
                    redis_client.lpop("processed_agent_data")
                )
                processed_agent_data_batch.append(processed_agent_data)
            saved = store_adapter.save_data(processed_agent_data_batch=processed_agent_data_batch)

            if(saved == False):
                logging.info("Error saving data to Store API")
                return {"status": "error"}
            
            logging.info("Processed agent data saved to the Store API")
        logging.info("Processed agent data saved to Redis")
        return {"status": "ok"}
    except Exception as e:
        logging.info(f"Error processing MQTT message: {e}")



client.on_connect = on_connect
client.on_message = on_message
client.connect(MQTT_BROKER_HOST, MQTT_BROKER_PORT)


client.loop_start()
