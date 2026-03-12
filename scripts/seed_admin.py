#!/usr/bin/env python3

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import bcrypt
from app.database import SessionLocal, engine, Base
from app.models.user import User

ADMIN_EMAIL = "admin@dev.local"
ADMIN_PASSWORD = "admin1234"
ADMIN_USERNAME = "admin"

Base.metadata.create_all(bind=engine)

db = SessionLocal()
try:
    existing = db.query(User).filter(User.email == ADMIN_EMAIL).first()
    if existing:
        print(f"Admin already exists: {ADMIN_EMAIL}")
    else:
        hashed = bcrypt.hashpw(ADMIN_PASSWORD.encode(), bcrypt.gensalt()).decode()
        admin = User(
            username=ADMIN_USERNAME,
            email=ADMIN_EMAIL,
            password=hashed,
            role="admin",
        )
        db.add(admin)
        db.commit()
finally:
    db.close()
