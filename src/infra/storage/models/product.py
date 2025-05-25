from sqlalchemy import Column, String, Text, Double, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PG_UUID

from src.infra.storage.db import Base


class ProductCategory(Base):
    __tablename__ = "product_categories"

    id = Column(PG_UUID(as_uuid=False), primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
    description = Column(Text, nullable=True)


class Product(Base):
    __tablename__ = "products"

    id = Column(PG_UUID(as_uuid=False), primary_key=True, index=True)
    name = Column(String, nullable=False)
    category_id = Column(
        PG_UUID(as_uuid=False),
        ForeignKey("product_categories.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    description = Column(Text, nullable=True)
    price = Column(Double, nullable=False)
