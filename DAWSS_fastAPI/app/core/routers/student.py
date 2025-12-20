from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List
from app.core.dependencies.database import get_db
from app.core.schemas.schemas import (
    TableResponse,
    BookingCreate,
    BookingResponse,
    StudentDashboard
)
from app.core.models.user import User
from app.core.models.seating import Table, Seat, Booking, SeatStatus
from app.core.utils.auth import get_current_active_user

router = APIRouter(prefix="/api/student", tags=["Student"])

@router.get("/dashboard", response_model=StudentDashboard)
async def get_student_dashboard(
        current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db)
):
    """Get student dashboard with booking info and available tables"""

    # Get user's booking if exists
    booking = db.query(Booking).filter(Booking.user_id == current_user.id).first()

    # Get all active tables with seats
    tables = db.query(Table).filter(Table.is_active == True).all()

    # Populate table_number for seats for UI convenience
    for table in tables:
        for seat in table.seats:
            if seat.table and hasattr(seat, "table"):
                setattr(seat, "table_number", seat.table.table_number)

    if booking and booking.seat and booking.seat.table:
        setattr(booking.seat, "table_number", booking.seat.table.table_number)

    return {
        "user": current_user,
        "booking": booking,
        "available_tables": tables
    }

@router.get("/tables", response_model=List[TableResponse])
async def get_available_tables(
        current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db)
):
    """Get all tables with seat availability"""
    tables = db.query(Table).filter(Table.is_active == True).all()
    # Populate table_number on seats
    for table in tables:
        for seat in table.seats:
            if seat.table:
                setattr(seat, "table_number", seat.table.table_number)
    return tables

@router.post("/book-seat", response_model=BookingResponse, status_code=status.HTTP_201_CREATED)
async def book_seat(
        booking_data: BookingCreate,
        current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db)
):
    """Book a seat for the current student"""

    # Check if user already has a booking
    existing_booking = db.query(Booking).filter(Booking.user_id == current_user.id).first()
    if existing_booking:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You already have a booking. Cancel it first to book another seat."
        )

    # Check if seat exists and is available
    seat = db.query(Seat).filter(Seat.id == booking_data.seat_id).first()
    if not seat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Seat not found"
        )

    if seat.status != SeatStatus.AVAILABLE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Seat is not available. Current status: {seat.status}"
        )

    # Create booking
    ticket_price = 50.00  # Set your ticket price
    new_booking = Booking(
        user_id=current_user.id,
        seat_id=seat.id,
        payment_status="pending",
        payment_amount=ticket_price
    )

    # Update seat status to selected
    seat.status = SeatStatus.SELECTED

    db.add(new_booking)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        # Likely seat_id uniqueness violation due to race
        # Reset seat to AVAILABLE if no booking persisted for it
        fresh = db.query(Booking).filter(Booking.seat_id == seat.id).first()
        if not fresh:
            seat.status = SeatStatus.AVAILABLE
            db.commit()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Seat was just taken by another user. Please pick a different seat."
        )

    db.refresh(new_booking)

    # populate table_number for response
    if new_booking.seat and new_booking.seat.table:
        setattr(new_booking.seat, "table_number", new_booking.seat.table.table_number)
    return new_booking

@router.delete("/cancel-booking/{booking_id}", status_code=status.HTTP_204_NO_CONTENT)
async def cancel_booking(
        booking_id: int,
        current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db)
):
    """Cancel a booking (only if not paid)"""

    booking = db.query(Booking).filter(
        Booking.id == booking_id,
        Booking.user_id == current_user.id
    ).first()

    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found"
        )

    if booking.payment_status == "completed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot cancel a paid booking. Contact admin for refunds."
        )

    # Free up the seat
    seat = db.query(Seat).filter(Seat.id == booking.seat_id).first()
    seat.status = SeatStatus.AVAILABLE

    db.delete(booking)
    db.commit()

    return None

@router.get("/my-booking", response_model=BookingResponse)
async def get_my_booking(
        current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db)
):
    """Get current user's booking details"""

    booking = db.query(Booking).filter(Booking.user_id == current_user.id).first()

    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No booking found"
        )

    # Populate table_number for response
    if booking.seat and booking.seat.table:
        setattr(booking.seat, "table_number", booking.seat.table.table_number)
    return booking