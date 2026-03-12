import bcrypt as _bcrypt
import factory
from factory.alchemy import SQLAlchemyModelFactory

from app.models.user import User

class UserFactory(SQLAlchemyModelFactory):
    class Meta:
        model = User
        sqlalchemy_session = None
        sqlalchemy_session_persistence = "commit"

    username = factory.Sequence(lambda n: f"User {n}")
    email = factory.Sequence(lambda n: f"user{n}@test.com")
    password = factory.LazyFunction(lambda: _bcrypt.hashpw(b"test123", _bcrypt.gensalt()).decode())
    role = "learner"
