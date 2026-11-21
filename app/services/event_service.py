from __future__ import annotations

import uuid
from typing import List, Dict, Any
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.models.event import SandboxActivityEvent
from app.models.session import SandboxSession
from app.schemas.event import ActivityEventItem, BatchEventsResponse
from app.core.exceptions import NotFoundException


class EventService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def ingest_batch(
        self,
        session_id: uuid.UUID,
        events: List[ActivityEventItem],
    ) -> BatchEventsResponse:
        stmt_session = select(SandboxSession).where(SandboxSession.id == session_id)
        res = await self.db.execute(stmt_session)
        session = res.scalar_one_or_none()
        if not session:
            raise NotFoundException(f"Sandbox session '{session_id}' not found.")

        # Find latest sequence number for monotonic ordering
        stmt_max_seq = select(func.max(SandboxActivityEvent.sequence_no)).where(
            SandboxActivityEvent.session_id == session_id
        )
        res_seq = await self.db.execute(stmt_max_seq)
        current_seq = res_seq.scalar() or 0

        now = datetime.now(timezone.utc)
        persisted = []

        for item in events:
            current_seq += 1
            event = SandboxActivityEvent(
                session_id=session_id,
                event_type=item.event_type,
                event_data=item.event_data,
                client_timestamp=item.client_timestamp,
                server_timestamp=now,
                sequence_no=current_seq,
            )
            self.db.add(event)
            persisted.append(event)

        await self.db.flush()

        return BatchEventsResponse(
            received_count=len(events),
            persisted_count=len(persisted),
            latest_sequence_no=current_seq,
        )
