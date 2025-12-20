"""
Database initialization script
Creates initial admin user and sample tables/seats
"""
from app.core.dependencies.database import SessionLocal, engine, Base
from app.core.models.user import User, UserRole
from app.core.models.seating import Table, Seat, SeatStatus
from app.core.utils.auth import get_password_hash

def init_database():
    # Create all tables
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()

    try:
        # Create admin user
        admin_exists = db.query(User).filter(User.email == "admin@prom.com").first()
        if not admin_exists:
            admin = User(
                email="admin@prom.com",
                hashed_password=get_password_hash("admin123"),
                full_name="System Administrator",
                role=UserRole.ADMIN,
                is_active=True
            )
            db.add(admin)
            print("✓ Created admin user (email: admin@prom.com, password: admin123)")

        # Create sample student
        student_exists = db.query(User).filter(User.email == "student@school.com").first()
        if not student_exists:
            student = User(
                email="student@school.com",
                hashed_password=get_password_hash("student123"),
                full_name="John Doe",
                student_id="STU001",
                role=UserRole.STUDENT,
                is_active=True
            )
            db.add(student)
            print("✓ Created sample student (email: student@school.com, password: student123)")

        # Create sample tables if they don't exist
        if db.query(Table).count() == 0:
            # Create 10 tables with 8 seats each
            for table_num in range(1, 11):
                section = "Main Floor" if table_num <= 6 else "Balcony"
                table = Table(
                    table_number=table_num,
                    capacity=8,
                    position_x=100.0 * (table_num % 3),
                    position_y=100.0 * (table_num // 3),
                    section=section,
                    is_active=True
                )
                db.add(table)
                db.flush()

                # Create seats for this table
                for seat_num in range(1, 9):
                    seat = Seat(
                        seat_number=seat_num,
                        table_id=table.id,
                        status=SeatStatus.AVAILABLE
                    )
                    db.add(seat)

            print("✓ Created 10 sample tables with 8 seats each (80 total seats)")

        db.commit()
        print("\n✅ Database initialization completed successfully!")
        print("\nYou can now:")
        print("1. Login as admin: admin@prom.com / admin123")
        print("2. Login as student: student@school.com / student123")
        print("3. Access API docs at: http://localhost:8000/docs")

    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("Initializing prom management database...")
    init_database()