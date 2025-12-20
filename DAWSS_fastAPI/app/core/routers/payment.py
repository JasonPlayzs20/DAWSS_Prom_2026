from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
from app.core.dependencies.database import get_db
from app.core.schemas.schemas import PaymentRequest, BookingResponse
from app.core.models.user import User
from app.core.models.seating import Booking, Seat, SeatStatus
from app.core.utils.auth import get_current_active_user
import uuid

router = APIRouter(prefix="/api/payment", tags=["Payment"])

@router.post("/process", response_model=BookingResponse)
async def process_payment(
        payment_data: PaymentRequest,
        current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db)
):
    """Process payment for a booking"""

    # Get the booking
    booking = db.query(Booking).filter(
        Booking.id == payment_data.booking_id,
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
            detail="Payment already completed"
        )

    # TODO: Integrate with actual payment gateway (Stripe, PayPal, etc.)
    # For now, simulate payment processing
    payment_success = process_payment_gateway(
        payment_data.payment_method,
        payment_data.payment_token,
        booking.payment_amount
    )

    if not payment_success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Payment processing failed"
        )

    # Update booking
    booking.payment_status = "completed"
    booking.payment_date = datetime.utcnow()
    booking.payment_transaction_id = str(uuid.uuid4())

    # Update seat status to reserved
    seat = db.query(Seat).filter(Seat.id == booking.seat_id).first()
    seat.status = SeatStatus.RESERVED

    db.commit()
    db.refresh(booking)

    # Populate table_number for response
    if booking.seat and booking.seat.table:
        setattr(booking.seat, "table_number", booking.seat.table.table_number)

    return booking

@router.get("/confirmation/{booking_id}", response_model=dict)
async def get_payment_confirmation(
        booking_id: int,
        current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db)
):
    """Get payment confirmation details"""

    booking = db.query(Booking).filter(
        Booking.id == booking_id,
        Booking.user_id == current_user.id
    ).first()

    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Booking not found"
        )

    return {
        "booking_id": booking.id,
        "payment_status": booking.payment_status,
        "payment_amount": booking.payment_amount,
        "transaction_id": booking.payment_transaction_id,
        "payment_date": booking.payment_date,
        "seat_info": {
            "seat_id": booking.seat.id,
            "seat_number": booking.seat.seat_number,
            "table_number": booking.seat.table.table_number
        }
    }

def process_payment_gateway(method: str, token: str, amount: float) -> bool:
    """
    Simulate payment processing with external gateway
    In production, integrate with Stripe, PayPal, Square, etc.
    """
    # Placeholder for payment gateway integration
    # Example with Stripe:
    # import stripe
    # stripe.api_key = "your_stripe_secret_key"
    # try:
    #     charge = stripe.Charge.create(
    #         amount=int(amount * 100),  # Convert to cents
    #         currency="usd",
    #         source=token,
    #         description="Prom Ticket Purchase"
    #     )
    #     return charge.paid
    # except stripe.error.CardError:
    #     return False

    # For now, always return True (simulate successful payment)
    return True