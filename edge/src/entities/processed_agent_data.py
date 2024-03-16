import datetime
from pydantic import BaseModel
from src.entities.agent_data import AgentData


class ProcessedAgentData(BaseModel):
    road_state: str
    agent_data: AgentData
    user_id: int
