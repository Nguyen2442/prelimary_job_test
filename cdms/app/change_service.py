from typing import Dict, List
from sqlalchemy import text
from sqlmodel import Session

from app.db import engine
from app.models import ChangeLog, InventoryItem, ProductState


def process_batch(items: List[InventoryItem], source: str) -> Dict[str, int]:
    summary = {"created": 0, "updated": 0, "duplicate": 0, "stale": 0}

    with Session(engine) as session, session.begin():
        session.exec(text("SELECT pg_advisory_xact_lock(1)"))

        for item in items:
            content = item.content()
            state = session.get(ProductState, item.sku)

            if state is None:
                state = ProductState(sku=item.sku, data=content, source_updated_at=item.lastUpdatedDate, version=1)
                summary["created"] += 1
            elif item.lastUpdatedDate < state.source_updated_at:
                summary["stale"] += 1
                continue
            elif content == state.data:
                summary["duplicate"] += 1
                continue
            else:
                state.data = content
                state.source_updated_at = item.lastUpdatedDate
                state.version += 1
                summary["updated"] += 1

            session.add(state)
            session.add(
                ChangeLog(
                    sku=item.sku,
                    version=state.version,
                    source=source,
                    data=content,
                    source_updated_at=item.lastUpdatedDate,
                )
            )
            session.flush()

    return summary
