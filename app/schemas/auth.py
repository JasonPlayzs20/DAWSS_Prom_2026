from pydantic import BaseModel

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class LoginSchema(BaseModel):
    email: str
    password: str