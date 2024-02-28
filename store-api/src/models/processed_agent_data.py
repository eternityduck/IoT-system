from models.agent_data import AgentData
from pydantic import BaseModel


class ProcessedAgentData(BaseModel):
    road_state: str
    agent_data: AgentData


class ProcessedAgentDataResponse(BaseModel):
    id: int
    road_state: str
    agent_data: AgentData
