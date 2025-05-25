from sqlalchemy import Column, Integer, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql import func

Base = declarative_base()


class InventoryUpdate(Base):
    __tablename__ = "inventory_updates"

    id = Column(PG_UUID(as_uuid=False), primary_key=True, nullable=False)
    product_id = Column(
        PG_UUID(as_uuid=False), ForeignKey("inventory_items.product_id"), nullable=False, index=True
    )
    quantity = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())


class InventoryItem(Base):
    __tablename__ = "inventory_items"

    product_id = Column(PG_UUID(as_uuid=False), primary_key=True, nullable=False, index=True)
    quantity = Column(Integer, nullable=False, default=0)
