from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.db.base import CRUDBase
from app.models.user import User
from app.db.schemas.user import UserCreate, UserUpdate
from app.db.utils import CipherManager 


class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    """CRUD class for the User model."""

    async def get_by_email(self, db: AsyncSession, *, email: str) -> User | None:
        """Retrieves a user by their email address."""
        statement = select(self.model).where(self.model.email == email)
        result = await db.execute(statement)
        return result.scalar_one_or_none()

    async def create(self, db: AsyncSession, *, obj_in: UserCreate) -> User:
        db_obj = self.model(
            email=obj_in.email,
            username=obj_in.username,
            # UPDATED USAGE: Call the static method on the class
            hashed_password=CipherManager.get_password_hash(obj_in.password)
        )
        db.add(db_obj)
        await db.flush()
        await db.refresh(db_obj)
        return db_obj


user = CRUDUser(User)