
# NOTE: Requires SQLAlchemy to be installed and available in your environment.
from app.core.dependencies.database import SessionLocal, Base, engine
from app.core.models.user import User, UserRole
from app.core.utils.auth import get_password_hash
from sqlalchemy.orm import Session

# -------------------
# CONFIGURE NEW USER
# -------------------
NAME = "Admin Account"
EMAIL = "s300054123@ddsbstudent.ca"
PASSWORD = "test123"  # plain-text, will be hashed
ROLE = "student"          # "admin" or "student"
STUDENT_ID = 300054123       # Optional for students
# -------------------

# 1️⃣ Create tables if they don't exist
Base.metadata.create_all(bind=engine)

# 2️⃣ Open a DB session
db: Session = SessionLocal()

try:
    # 3️⃣ Check if user already exists
    existing_user = db.query(User).filter(User.email == EMAIL).first()
    if existing_user:
        print(f"User {EMAIL} already exists.")
    else:
        # 4️⃣ Create and add user
        user = User(
            full_name=NAME,
            email=EMAIL,
            hashed_password=get_password_hash(PASSWORD),
            role=UserRole.ADMIN if ROLE == "admin" else UserRole.STUDENT,
            student_id=STUDENT_ID,
            is_active=True
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        print(f"✅ User {EMAIL} added successfully.")

finally:
    db.close()
