from typing import Optional
from datetime import datetime

from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import registry


mapper_registry = registry()


@mapper_registry.mapped
class ProcessedAgentDataInDB:
    __tablename__ = "processed_agent_data"

    id: Mapped[Optional[int]] = mapped_column(primary_key=True)
    road_state: Mapped[str]
    user_id: Mapped[int]
    x: Mapped[float]
    y: Mapped[float]
    z: Mapped[float]
    latitude: Mapped[float]
    longitude: Mapped[float]
    timestamp: Mapped[datetime]
