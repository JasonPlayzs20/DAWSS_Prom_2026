from sqlalchemy import Column, Integer, Boolean, ForeignKey
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Seat(Base):
    __tablename__ = "seats"

    id = Column(Integer, primary_key=True, index=True)
    taken = Column(Boolean, default=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    locked = Column(Boolean, default=False)
