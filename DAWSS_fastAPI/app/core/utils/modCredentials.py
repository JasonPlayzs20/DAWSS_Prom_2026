"""
Utility script to modify user credentials
Can be run from command line or imported
"""
import sys
from sqlalchemy.orm import Session
from app.core.dependencies.database import SessionLocal
from app.core.models.user import User, UserRole
from app.core.utils.auth import get_password_hash

def modify_user(
        identifier: str,
        by_email: bool = True,
        new_email: str = None,
        new_password: str = None,
        new_full_name: str = None,
        new_role: str = None,
        new_student_id: str = None,
        activate: bool = None,
        db: Session = None
) -> User:
    """
    Modify user credentials and information

    Args:
        identifier: Email or student_id to search for
        by_email: If True, search by email; if False, search by student_id
        new_email: New email address (optional)
        new_password: New password (optional)
        new_full_name: New full name (optional)
        new_role: New role - "student" or "admin" (optional)
        new_student_id: New student ID (optional)
        activate: Set account active status (optional)
        db: Database session (optional)

    Returns:
        Updated User object

    Raises:
        ValueError: If user not found or invalid data
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

        print(f"\nFound user: {user.email} ({user.full_name})")

        changes_made = []

        # Update email
        if new_email and new_email != user.email:
            # Check if new email already exists
            existing = db.query(User).filter(User.email == new_email).first()
            if existing:
                raise ValueError(f"Email '{new_email}' already in use")
            user.email = new_email
            changes_made.append(f"email -> {new_email}")

        # Update password
        if new_password:
            user.hashed_password = get_password_hash(new_password)
            changes_made.append("password updated")

        # Update full name
        if new_full_name and new_full_name != user.full_name:
            user.full_name = new_full_name
            changes_made.append(f"name -> {new_full_name}")

        # Update role
        if new_role and new_role != user.role:
            if new_role not in ["student", "admin"]:
                raise ValueError(f"Invalid role: {new_role}")
            user.role = UserRole.ADMIN if new_role == "admin" else UserRole.STUDENT
            changes_made.append(f"role -> {new_role}")

        # Update student ID
        if new_student_id and new_student_id != user.student_id:
            # Check if new student_id already exists
            existing = db.query(User).filter(User.student_id == new_student_id).first()
            if existing:
                raise ValueError(f"Student ID '{new_student_id}' already in use")
            user.student_id = new_student_id
            changes_made.append(f"student_id -> {new_student_id}")

        # Update active status
        if activate is not None and activate != user.is_active:
            user.is_active = activate
            status = "activated" if activate else "deactivated"
            changes_made.append(f"account {status}")

        if not changes_made:
            print("⚠ No changes were made")
            return user

        db.commit()
        db.refresh(user)

        print(f"\n✅ Successfully updated user:")
        for change in changes_made:
            print(f"  • {change}")

        return user

    except Exception as e:
        db.rollback()
        print(f"❌ Error modifying user: {e}")
        raise

    finally:
        if should_close:
            db.close()

def reset_password(identifier: str, new_password: str, by_email: bool = True, db: Session = None):
    """Quick function to reset a user's password"""
    return modify_user(identifier, by_email, new_password=new_password, db=db)

def toggle_active_status(identifier: str, by_email: bool = True, db: Session = None):
    """Quick function to toggle user active status"""
    should_close = False
    if db is None:
        db = SessionLocal()
        should_close = True

    try:
        if by_email:
            user = db.query(User).filter(User.email == identifier).first()
        else:
            user = db.query(User).filter(User.student_id == identifier).first()

        if not user:
            raise ValueError(f"User not found: {identifier}")

        new_status = not user.is_active
        return modify_user(identifier, by_email, activate=new_status, db=db)

    finally:
        if should_close:
            db.close()

def main():
    """Command line interface for modifying credentials"""
    print("=== Modify User Credentials ===\n")

    try:
        # Get user to modify
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

        print("\n--- What would you like to modify? (press Enter to skip) ---\n")

        new_email = input("New email: ").strip() or None
        new_password = input("New password: ").strip() or None
        new_full_name = input("New full name: ").strip() or None
        new_role = input("New role (student/admin): ").strip().lower() or None
        new_student_id = input("New student ID: ").strip() or None

        activate_input = input("Activate account? (yes/no/skip) [skip]: ").strip().lower()
        activate = None
        if activate_input == "yes":
            activate = True
        elif activate_input == "no":
            activate = False

        # Check if any changes were requested
        if not any([new_email, new_password, new_full_name, new_role, new_student_id, activate is not None]):
            print("❌ No changes requested!")
            return

        # Confirm changes
        print("\n⚠ About to make the following changes:")
        if new_email:
            print(f"  • Email: {new_email}")
        if new_password:
            print(f"  • Password: ******")
        if new_full_name:
            print(f"  • Full Name: {new_full_name}")
        if new_role:
            print(f"  • Role: {new_role}")
        if new_student_id:
            print(f"  • Student ID: {new_student_id}")
        if activate is not None:
            print(f"  • Active: {activate}")

        confirm = input("\nProceed? (yes/no): ").strip().lower()
        if confirm != "yes":
            print("❌ Operation cancelled")
            return

        # Modify user
        modify_user(
            identifier=identifier,
            by_email=by_email,
            new_email=new_email,
            new_password=new_password,
            new_full_name=new_full_name,
            new_role=new_role,
            new_student_id=new_student_id,
            activate=activate
        )

    except KeyboardInterrupt:
        print("\n\n⚠ Operation cancelled")
    except Exception as e:
        print(f"\n❌ Failed to modify user: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()