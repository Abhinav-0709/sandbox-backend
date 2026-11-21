from __future__ import annotations

import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime
from pydantic import BaseModel, Field


class ActivityEventItem(BaseModel):
    event_type: str = Field(..., description="Telemetry event type, e.g. spreadsheet.cell_changed")
    event_data: Dict[str, Any] = Field(default_factory=dict)
    client_timestamp: Optional[datetime] = None
    sequence_no: Optional[int] = None


class BatchEventsRequest(BaseModel):
    events: List[ActivityEventItem] = Field(..., description="Array of telemetry events")


class BatchEventsResponse(BaseModel):
    received_count: int
    persisted_count: int
    latest_sequence_no: int
