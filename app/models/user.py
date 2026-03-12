from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func

from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String(100), nullable=False)
    company = Column(String(100), nullable=True)
    email = Column(String(320), nullable=False, unique=True)
    password = Column(Text, nullable=False)
    role = Column(String(20), default="learner")
    created_at = Column(DateTime, server_default=func.now())
