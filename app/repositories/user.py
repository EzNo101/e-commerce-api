from typing import Any
from sqlalchemy import select, or_, exists
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User


class UserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, user_id: int) -> User | None:
        return await self.session.get(User, user_id)

    async def get_by_email(self, email: str) -> User | None:
        result = await self.session.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def exists_by_email(self, email: str) -> bool:
        result = await self.session.execute(select(exists().where(User.email == email)))
        return result.scalar_one()

    async def exists_by_username(self, username: str):
        result = await self.session.execute(
            select(exists().where(User.username == username))
        )
        return result.scalar_one()

    async def exists_by_email_or_username(self, email: str, username: str) -> bool:
        result = await self.session.execute(
            select(exists().where(or_(User.email == email, User.username == username)))
        )
        return result.scalar_one()

    async def create_user(
        self,
        username: str,
        email: str,
        hashed_password: str,
        is_active: bool,
        is_admin: bool,
    ) -> User:
        user = User(
            username=username,
            email=email,
            hashed_password=hashed_password,
            is_active=is_active,
            is_admin=is_admin,
        )
        self.session.add(user)
        await self.session.flush()
        return user

    async def update_user(self, user: User, updates: dict[str, Any]) -> User:
        for field, value in updates.items():
            setattr(user, field, value)

        return user

    async def change_password(self, user: User, new_password_hash: str) -> User:
        user.hashed_password = new_password_hash
        return user

    async def delete_user(self, user: User) -> None:
        await self.session.delete(user)
