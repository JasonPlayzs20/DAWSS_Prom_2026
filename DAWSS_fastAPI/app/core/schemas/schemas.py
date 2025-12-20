from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

# Enums
class UserRole(str, Enum):
    STUDENT = "student"
    ADMIN = "admin"

class SeatStatus(str, Enum):
    AVAILABLE = "available"
    SELECTED = "selected"
    RESERVED = "reserved"
    BLOCKED = "blocked"

# User Schemas
class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    student_id: Optional[str] = None

class UserCreate(UserBase):
    password: str
    role: UserRole = UserRole.STUDENT

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(UserBase):
    id: int
    role: UserRole
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

# Token Schemas
class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse

# Seat Schemas
class SeatBase(BaseModel):
    seat_number: int
    table_id: int

class SeatResponse(SeatBase):
    id: int
    status: SeatStatus
    # expose table_number for UI without requiring nested table serialization
    table_number: Optional[int] = None

    class Config:
        from_attributes = True

# Table Schemas
class TableBase(BaseModel):
    table_number: int
    capacity: int
    position_x: Optional[float] = None
    position_y: Optional[float] = None
    section: Optional[str] = None

class TableCreate(TableBase):
    pass

class TableResponse(TableBase):
    id: int
    is_active: bool
    seats: List[SeatResponse] = []

    class Config:
        from_attributes = True

# Booking Schemas
class BookingCreate(BaseModel):
    seat_id: int

class BookingResponse(BaseModel):
    id: int
    user_id: int
    seat_id: int
    payment_status: str
    payment_amount: float
    booking_date: datetime
    payment_date: Optional[datetime] = None
    seat: SeatResponse

    class Config:
        from_attributes = True

class PaymentRequest(BaseModel):
    booking_id: int
    payment_method: str  # e.g., "credit_card", "stripe"
    payment_token: str

# Admin Schemas
class AdminSeatUpdate(BaseModel):
    seat_id: int
    status: SeatStatus

class AdminAssignSeat(BaseModel):
    user_id: int
    seat_id: int

# Dashboard Schemas
class StudentDashboard(BaseModel):
    user: UserResponse
    booking: Optional[BookingResponse] = None
    available_tables: List[TableResponse]

class AdminDashboardStats(BaseModel):
    total_seats: int
    available_seats: int
    reserved_seats: int
    pending_payments: int
    total_revenue: float
    tables: List[TableResponse]