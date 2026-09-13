from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from sqlalchemy import String, ForeignKey, DateTime, Integer, Text, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from .base import Base


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True)
    customer_id: Mapped[int] = mapped_column(ForeignKey("customers.id"), nullable=False)

    status: Mapped[str] = mapped_column(String(50), default="CART")

    # Datos de pago
    payment_method: Mapped[Optional[str]] = mapped_column(String(50))
    payment_ref: Mapped[Optional[str]] = mapped_column(String(255))
    exchange_rate: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2))

    # Datos de entrega (Relación e histórico)
    municipality_id: Mapped[Optional[int]] = mapped_column(ForeignKey("municipalities.id", ondelete="SET NULL"))
    municipality_name: Mapped[Optional[str]] = mapped_column(String(100))
    delivery_fee_eur: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2))
    delivery_maps: Mapped[Optional[str]] = mapped_column(Text)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), onupdate=func.now())

    customer: Mapped["Customer"] = relationship(back_populates="orders")
    municipality: Mapped[Optional["Municipality"]] = relationship()
    items: Mapped[List["OrderItem"]] = relationship(back_populates="order", cascade="all, delete-orphan")


class OrderItem(Base):
    __tablename__ = "order_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"), nullable=False)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, default=1)

    protein: Mapped[Optional[str]] = mapped_column(String(50))
    notes: Mapped[Optional[str]] = mapped_column(Text)

    order: Mapped["Order"] = relationship(back_populates="items")
    product: Mapped["Product"] = relationship(back_populates="order_items")
    extras: Mapped[List["OrderItemExtra"]] = relationship(back_populates="order_item", cascade="all, delete-orphan")


class OrderItemExtra(Base):
    __tablename__ = "order_item_extras"

    order_item_id: Mapped[int] = mapped_column(ForeignKey("order_items.id", ondelete="CASCADE"), primary_key=True)
    extra_id: Mapped[int] = mapped_column(ForeignKey("extras.id"), primary_key=True)
    quantity: Mapped[int] = mapped_column(Integer, default=1)

    order_item: Mapped["OrderItem"] = relationship(back_populates="extras")
    extra: Mapped["Extra"] = relationship()