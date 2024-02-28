from config import DATABASE_URL
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from sqlalchemy import (
    create_engine,
)
from sqlalchemy.orm import sessionmaker, Session
from models.processed_agent_data import ProcessedAgentData
from models.processed_agent_data import ProcessedAgentDataResponse
from entities.processed_agent_data import ProcessedAgentDataInDB
from utils.ws import WebSocketClient
from typing import List
import uvicorn

app = FastAPI()
wsClient = WebSocketClient()

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(bind=engine)
session = Session(engine)


@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: int):
    await websocket.accept()
    if user_id not in wsClient.subscriptions:
        wsClient.subscriptions[user_id] = set()
    wsClient.subscriptions[user_id].add(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        wsClient.subscriptions[user_id].remove(websocket)


@app.post("/processed_agent_data/")
async def create_processed_agent_data(data: List[ProcessedAgentData]):
    mapped_data = [
        ProcessedAgentDataInDB(
            road_state=d.road_state,
            user_id=d.agent_data.user_id,
            x=d.agent_data.accelerometer.x,
            y=d.agent_data.accelerometer.y,
            z=d.agent_data.accelerometer.z,
            latitude=d.agent_data.gps.latitude,
            longitude=d.agent_data.gps.longitude,
            timestamp=d.agent_data.timestamp,
        )
        for d in data
    ]
    session.add_all(mapped_data)
    try:
        session.commit()
    except:
        session.rollback()
        raise HTTPException(status_code=500, detail="Error saving data")

    [wsClient.send_data_to_subscribers(d.agent_data.user_id, data) for d in data]
    return data


@app.get(
    "/processed_agent_data/{processed_agent_data_id}",
    response_model=ProcessedAgentDataResponse,
)
def read_processed_agent_data(processed_agent_data_id: int):
    try:
        result = session.get(ProcessedAgentDataInDB, processed_agent_data_id)
    except:
        raise HTTPException(status_code=404, detail="ProcessedAgentData not found")
    return ProcessedAgentDataResponse(
        id=result.id,
        road_state=result.road_state,
        agent_data={
            "user_id": result.user_id,
            "accelerometer": {"x": result.x, "y": result.y, "z": result.z},
            "gps": {"latitude": result.latitude, "longitude": result.longitude},
            "timestamp": result.timestamp,
        },
    )


@app.get("/processed_agent_data/", response_model=list[ProcessedAgentData])
def list_processed_agent_data():
    result = session.query(ProcessedAgentDataInDB).all()
    return [
        ProcessedAgentDataResponse(
            id=r.id,
            road_state=r.road_state,
            agent_data={
                "user_id": r.user_id,
                "accelerometer": {"x": r.x, "y": r.y, "z": r.z},
                "gps": {"latitude": r.latitude, "longitude": r.longitude},
                "timestamp": r.timestamp,
            },
        )
        for r in result
    ]


@app.put(
    "/processed_agent_data/{processed_agent_data_id}",
    response_model=ProcessedAgentDataResponse,
)
def update_processed_agent_data(processed_agent_data_id: int, data: ProcessedAgentData):

    agent_db = session.get(ProcessedAgentDataInDB, processed_agent_data_id)

    if agent_db is None:
        raise HTTPException(status_code=404, detail="ProcessedAgentData not found")

    session.query(ProcessedAgentDataInDB).filter(
        ProcessedAgentDataInDB.id == processed_agent_data_id
    ).update(
        {
            "road_state": data.road_state,
            "user_id": data.agent_data.user_id,
            "x": data.agent_data.accelerometer.x,
            "y": data.agent_data.accelerometer.y,
            "z": data.agent_data.accelerometer.z,
            "latitude": data.agent_data.gps.latitude,
            "longitude": data.agent_data.gps.longitude,
            "timestamp": data.agent_data.timestamp,
        }
    )
    session.commit()

    result = session.get(ProcessedAgentDataInDB, processed_agent_data_id)

    return ProcessedAgentDataResponse(
        id=result.id,
        road_state=result.road_state,
        agent_data={
            "user_id": result.user_id,
            "accelerometer": {"x": result.x, "y": result.y, "z": result.z},
            "gps": {"latitude": result.latitude, "longitude": result.longitude},
            "timestamp": result.timestamp,
        },
    )


@app.delete(
    "/processed_agent_data/{processed_agent_data_id}",
    response_model=ProcessedAgentDataResponse,
)
def delete_processed_agent_data(processed_agent_data_id: int):
    try:
        result = session.get(ProcessedAgentDataInDB, processed_agent_data_id)
    except:
        raise HTTPException(status_code=404, detail="ProcessedAgentData not found")
    session.delete(result)
    session.commit()
    return ProcessedAgentDataResponse(
        id=result.id,
        road_state=result.road_state,
        agent_data={
            "user_id": result.user_id,
            "accelerometer": {"x": result.x, "y": result.y, "z": result.z},
            "gps": {"latitude": result.latitude, "longitude": result.longitude},
            "timestamp": result.timestamp,
        },
    )


if __name__ == "__main__":

    uvicorn.run(app, host="127.0.0.1", port=8000)
