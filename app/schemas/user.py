from pydantic import BaseModel

class UserBase(BaseModel):
    email: str
    password: str
    can_select: bool = False
    has_guest: bool = False
class UserOut(BaseModel):
    username: str
    # password: str
    can_select: bool = False
    has_guest: bool = False
    class Config:
        orm_mode = True