from pydantic import BaseModel

class SeatSelectRequest(BaseModel):
    seat_id: int

class SeatOut(BaseModel):
    id: int
    taken: bool
    user_id: int | None
    locked: bool = False

    class Config:
        orm_mode = True
