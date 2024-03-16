import datetime
from src.entities.agent_data import AgentData
from src.entities.processed_agent_data import ProcessedAgentData


def process_agent_data(
    agent_data: AgentData, user_id: int, timestamp: datetime
) -> ProcessedAgentData:
    """
    Process agent data and classify the state of the road surface.
    Parameters:
        agent_data (AgentData): Agent data that containing accelerometer, GPS, and timestamp.
    Returns:
        processed_data_batch (ProcessedAgentData): Processed data containing the classified state of the road surface and agent data.
    """
    road_state = (
        "good"
        if agent_data.accelerometer.z > 0 and agent_data.accelerometer.x > 0
        else "bad"
    )
    return ProcessedAgentData(
        road_state=road_state,
        agent_data=agent_data,
        user_id=user_id,
        timestamp=timestamp,
    )
