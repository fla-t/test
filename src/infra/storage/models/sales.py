import uuid
from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Sale(Base):
    __tablename__ = "sales"

    id = Column(
        PG_UUID(as_uuid=False), primary_key=True, default=uuid.uuid4, nullable=False, index=True
    )
    product_id = Column(
        PG_UUID(as_uuid=False),
        ForeignKey("products.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    quantity = Column(Integer, nullable=False)
    total_price = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False)
