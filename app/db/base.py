from app.db.session import engine
from app.models.user import User
from app.models.seat import Seat

def init_db():
    User.metadata.create_all(bind=engine)
    Seat.metadata.create_all(bind=engine)
