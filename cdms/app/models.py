from datetime import datetime, timezone
from typing import Any, Dict, Optional
from pydantic import AwareDatetime, BaseModel
from sqlalchemy import Column, DateTime, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field, SQLModel


class InventoryItem(BaseModel):
    sku: str
    partnerSKU: str
    warehouseCode: str
    physicalQty: int
    availableQty: int
    pendingInQty: int
    pendingOutQty: int
    freezeQty: int
    lastUpdatedDate: AwareDatetime

    def content(self) -> Dict[str, Any]:
        return self.model_dump(exclude={"lastUpdatedDate"})


class ProductState(SQLModel, table=True):
    __tablename__ = "product_state"

    sku: str = Field(primary_key=True)
    data: Dict[str, Any] = Field(sa_column=Column(JSONB, nullable=False))
    source_updated_at: datetime = Field(sa_column=Column(DateTime(timezone=True), nullable=False))
    version: int


class ChangeLog(SQLModel, table=True):
    __tablename__ = "change_log"
    __table_args__ = (UniqueConstraint("sku", "version"),)

    id: Optional[int] = Field(default=None, primary_key=True)
    sku: str = Field(index=True)
    version: int
    source: str
    data: Dict[str, Any] = Field(sa_column=Column(JSONB, nullable=False))
    source_updated_at: datetime = Field(sa_column=Column(DateTime(timezone=True), nullable=False))
    recorded_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )
