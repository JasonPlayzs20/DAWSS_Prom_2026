from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Float, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
from sqlalchemy import DateTime
import enum
from app.core.dependencies.database import Base

class SeatStatus(str, enum.Enum):
    AVAILABLE = "available"
    SELECTED = "selected"  # Selected but not paid
    RESERVED = "reserved"  # Paid and confirmed
    BLOCKED = "blocked"    # Admin blocked

class Table(Base):
    __tablename__ = "tables"

    id = Column(Integer, primary_key=True, index=True)
    table_number = Column(Integer, unique=True, nullable=False)
    capacity = Column(Integer, nullable=False)
    position_x = Column(Float)  # For visual layout
    position_y = Column(Float)  # For visual layout
    is_active = Column(Boolean, default=True)
    section = Column(String)  # e.g., "Main Floor", "Balcony"

    # Relationships
    seats = relationship("Seat", back_populates="table", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Table {self.table_number}>"

class Seat(Base):
    __tablename__ = "seats"

    id = Column(Integer, primary_key=True, index=True)
    seat_number = Column(Integer, nullable=False)
    table_id = Column(Integer, ForeignKey("tables.id"), nullable=False)
    status = Column(Enum(SeatStatus), default=SeatStatus.AVAILABLE, nullable=False)

    # Relationships
    table = relationship("Table", back_populates="seats")
    booking = relationship("Booking", back_populates="seat", uselist=False)

    def __repr__(self):
        return f"<Seat {self.seat_number} at Table {self.table_id}>"

class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    seat_id = Column(Integer, ForeignKey("seats.id"), nullable=False, unique=True)
    payment_status = Column(String, default="pending")  # pending, completed, failed
    payment_amount = Column(Float, nullable=False)
    payment_transaction_id = Column(String, unique=True)
    booking_date = Column(DateTime, default=datetime.utcnow())
    payment_date = Column(DateTime)

    # Relationships
    user = relationship("User", back_populates="booking")
    seat = relationship("Seat", back_populates="booking")

    def __repr__(self):
        return f"<Booking user={self.user_id} seat={self.seat_id} status={self.payment_status}>"
