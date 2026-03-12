from fastapi import Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User

class UserService:
    def __init__(self, db: Session = Depends(get_db)):
        self.db = db

    def get_by_email(self, email: str) -> User | None:
        return self.db.query(User).filter(User.email == email).first()

    def get_by_id(self, user_id: int) -> User | None:
        return self.db.query(User).filter(User.id == user_id).first()
