import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    DATABASE_URL = os.getenv("DATABASE_URL","sqlite:///./database.db")
    JWT_SECRET = os.getenv("JWT_SECRET", "26PROM")
    JWT_ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 60*24

settings = Config()

