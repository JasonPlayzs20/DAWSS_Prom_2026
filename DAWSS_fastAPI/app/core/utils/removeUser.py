"""
Utility script to remove users from the database
Can be run from command line or imported
"""
import sys
from sqlalchemy.orm import Session
from app.core.dependencies.database import SessionLocal
from app.core.models.user import User
from app.core.models.seating import Booking, Seat, SeatStatus

def remove_user(
        identifier: str,
        by_email: bool = True,
        db: Session = None
) -> bool:
    """
    Remove a user from the database

    Args:
        identifier: Email or student_id to search for
        by_email: If True, search by email; if False, search by student_id
        db: Database session (optional, will create if not provided)

    Returns:
        True if successful, False otherwise

    Raises:
        ValueError: If user not found or has dependencies
    """
    # Create db session if not provided
    should_close = False
    if db is None:
        db = SessionLocal()
        should_close = True

    try:
        # Find user
        if by_email:
            user = db.query(User).filter(User.email == identifier).first()
        else:
            user = db.query(User).filter(User.student_id == identifier).first()

        if not user:
            raise ValueError(f"User not found: {identifier}")

        # Check for existing bookings
        booking = db.query(Booking).filter(Booking.user_id == user.id).first()

        if booking:
            print(f"⚠ User has an active booking (Seat ID: {booking.seat_id})")
            confirm = input("Delete booking and free seat? (yes/no): ").strip().lower()

            if confirm != "yes":
                print("❌ Operation cancelled")
                return False

            # Free up the seat
            seat = db.query(Seat).filter(Seat.id == booking.seat_id).first()
            if seat:
                seat.status = SeatStatus.AVAILABLE

            # Delete booking
            db.delete(booking)
            print("✓ Deleted booking and freed seat")

        # Delete user
        user_email = user.email
        user_role = user.role
        db.delete(user)
        db.commit()

        print(f"✅ Successfully removed user: {user_email} ({user_role})")
        return True

    except Exception as e:
        db.rollback()
        print(f"❌ Error removing user: {e}")
        raise

    finally:
        if should_close:
            db.close()

def list_users(db: Session = None):
    """List all users in the database"""
    should_close = False
    if db is None:
        db = SessionLocal()
        should_close = True

    try:
        users = db.query(User).all()

        if not users:
            print("No users found in database")
            return

        print("\n=== All Users ===")
        print(f"{'ID':<5} {'Email':<30} {'Name':<25} {'Role':<10} {'Student ID':<15}")
        print("-" * 90)

        for user in users:
            print(f"{user.id:<5} {user.email:<30} {user.full_name:<25} {user.role:<10} {user.student_id or 'N/A':<15}")

        print(f"\nTotal users: {len(users)}\n")

    finally:
        if should_close:
            db.close()

def main():
    """Command line interface for removing users"""
    print("=== Remove User ===\n")

    try:
        # Option to list users first
        list_option = input("List all users first? (yes/no) [yes]: ").strip().lower()
        if list_option != "no":
            list_users()

        # Get search method
        search_method = input("Search by (email/id) [email]: ").strip().lower() or "email"

        if search_method == "email":
            identifier = input("Enter email: ").strip()
            by_email = True
        else:
            identifier = input("Enter student ID: ").strip()
            by_email = False

        if not identifier:
            print("❌ Identifier is required!")
            return

        # Confirm deletion
        print(f"\n⚠ WARNING: This will permanently delete the user!")
        confirm = input("Are you sure? (yes/no): ").strip().lower()

        if confirm != "yes":
            print("❌ Operation cancelled")
            return

        # Remove user
        remove_user(identifier, by_email)

    except KeyboardInterrupt:
        print("\n\n⚠ Operation cancelled")
    except Exception as e:
        print(f"\n❌ Failed to remove user: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()