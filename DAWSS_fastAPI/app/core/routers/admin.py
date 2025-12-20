from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from sqlalchemy import func
from app.core.dependencies.database import get_db
from app.core.schemas.schemas import (
    TableCreate,
    TableResponse,
    AdminDashboardStats,
    AdminSeatUpdate,
    AdminAssignSeat,
    BookingResponse
)
from app.core.models.user import User
from app.core.models.seating import Table, Seat, Booking, SeatStatus
from app.core.utils.auth import get_current_admin

router = APIRouter(prefix="/api/admin", tags=["Admin"])

@router.get("/dashboard", response_model=AdminDashboardStats)
async def get_admin_dashboard(
        current_admin: User = Depends(get_current_admin),
        db: Session = Depends(get_db)
):
    """Get admin dashboard statistics"""

    total_seats = db.query(Seat).count()
    available_seats = db.query(Seat).filter(Seat.status == SeatStatus.AVAILABLE).count()
    reserved_seats = db.query(Seat).filter(Seat.status == SeatStatus.RESERVED).count()
    pending_payments = db.query(Booking).filter(Booking.payment_status == "pending").count()

    total_revenue = db.query(func.sum(Booking.payment_amount)).filter(
        Booking.payment_status == "completed"
    ).scalar() or 0.0

    tables = db.query(Table).all()

    return {
        "total_seats": total_seats,
        "available_seats": available_seats,
        "reserved_seats": reserved_seats,
        "pending_payments": pending_payments,
        "total_revenue": total_revenue,
        "tables": tables
    }

@router.post("/tables", response_model=TableResponse, status_code=status.HTTP_201_CREATED)
async def create_table(
        table_data: TableCreate,
        current_admin: User = Depends(get_current_admin),
        db: Session = Depends(get_db)
):
    """Create a new table with seats"""

    # Check if table number already exists
    existing_table = db.query(Table).filter(Table.table_number == table_data.table_number).first()
    if existing_table:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Table number already exists"
        )

    # Create table
    new_table = Table(
        table_number=table_data.table_number,
        capacity=table_data.capacity,
        position_x=table_data.position_x,
        position_y=table_data.position_y,
        section=table_data.section
    )

    db.add(new_table)
    db.flush()  # Get the table ID

    # Create seats for the table
    for seat_num in range(1, table_data.capacity + 1):
        seat = Seat(
            seat_number=seat_num,
            table_id=new_table.id,
            status=SeatStatus.AVAILABLE
        )
        db.add(seat)

    db.commit()
    db.refresh(new_table)

    return new_table

@router.put("/seats/{seat_id}/status", response_model=dict)
async def update_seat_status(
        seat_id: int,
        seat_update: AdminSeatUpdate,
        current_admin: User = Depends(get_current_admin),
        db: Session = Depends(get_db)
):
    """Update seat status (admin override)"""

    seat = db.query(Seat).filter(Seat.id == seat_id).first()
    if not seat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Seat not found"
        )

    seat.status = seat_update.status
    db.commit()

    return {"message": "Seat status updated successfully", "seat_id": seat_id, "new_status": seat_update.status}

@router.post("/assign-seat", response_model=BookingResponse)
async def admin_assign_seat(
        assignment: AdminAssignSeat,
        current_admin: User = Depends(get_current_admin),
        db: Session = Depends(get_db)
):
    """Manually assign a seat to a user"""

    # Check if user exists
    user = db.query(User).filter(User.id == assignment.user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Check if user already has a booking
    existing_booking = db.query(Booking).filter(Booking.user_id == assignment.user_id).first()
    if existing_booking:
        # Update existing booking
        old_seat = db.query(Seat).filter(Seat.id == existing_booking.seat_id).first()
        old_seat.status = SeatStatus.AVAILABLE

        existing_booking.seat_id = assignment.seat_id
        new_seat = db.query(Seat).filter(Seat.id == assignment.seat_id).first()
        new_seat.status = SeatStatus.RESERVED

        db.commit()
        db.refresh(existing_booking)
        return existing_booking

    # Create new booking
    seat = db.query(Seat).filter(Seat.id == assignment.seat_id).first()
    if not seat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Seat not found"
        )

    new_booking = Booking(
        user_id=assignment.user_id,
        seat_id=assignment.seat_id,
        payment_status="completed",  # Admin assigned = auto-paid
        payment_amount=50.00
    )

    seat.status = SeatStatus.RESERVED

    db.add(new_booking)
    db.commit()
    db.refresh(new_booking)

    return new_booking

@router.get("/bookings", response_model=List[BookingResponse])
async def get_all_bookings(
        current_admin: User = Depends(get_current_admin),
        db: Session = Depends(get_db)
):
    """Get all bookings"""
    bookings = db.query(Booking).all()
    return bookings

@router.delete("/tables/{table_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_table(
        table_id: int,
        current_admin: User = Depends(get_current_admin),
        db: Session = Depends(get_db)
):
    """Delete a table and its seats"""

    table = db.query(Table).filter(Table.id == table_id).first()
    if not table:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Table not found"
        )

    # Check if any seats are reserved
    reserved_seats = db.query(Seat).filter(
        Seat.table_id == table_id,
        Seat.status == SeatStatus.RESERVED
    ).count()

    if reserved_seats > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete table with reserved seats"
        )

    db.delete(table)
    db.commit()

    return None