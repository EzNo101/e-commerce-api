from app.db.uow import UnitOfWork
from app.repositories.user import UserRepository
from app.models.user import User
from app.schemas.user import UserUpdate, ChangePasswordRequest
from app.core.security import get_password_hash, verify_password


class UserService:
    async def get_by_id(self, user_id: int, uow: UnitOfWork) -> User:
        repo = UserRepository(uow.session)

        user = await repo.get_by_id(user_id)
        if user is None:
            raise ValueError("User not found")

        return user

    async def get_by_email(self, email: str, uow: UnitOfWork) -> User:
        repo = UserRepository(uow.session)

        user = await repo.get_by_email(email)
        if not user:
            raise ValueError("User not found")

        return user

    async def update_profile(
        self, user: User, data: UserUpdate, uow: UnitOfWork
    ) -> User:
        repo = UserRepository(uow.session)

        updates = data.model_dump(exclude_unset=True, exclude_none=True)

        if not updates:
            return user

        if "email" in updates and user.email != updates["email"]:
            email_exists = await repo.exists_by_email(updates["email"])
            if email_exists:
                raise ValueError("Email already in use")
        if "username" in updates and user.username != updates["username"]:
            username_exists = await repo.exists_by_username(updates["username"])
            if username_exists:
                raise ValueError("Username already in use")

        user = await repo.update_user(user, updates)
        await uow.commit()
        await uow.refresh(user)

        return user

    async def change_password(
        self, user: User, data: ChangePasswordRequest, uow: UnitOfWork
    ) -> User:
        repo = UserRepository(uow.session)

        if not verify_password(data.current_password, user.hashed_password):
            raise ValueError("Invalid password")

        if verify_password(data.new_password, user.hashed_password):
            raise ValueError("New password must be different from current password")

        new_password_hash = get_password_hash(data.new_password)

        await repo.change_password(user, new_password_hash)
        await uow.commit()
        await uow.refresh(user)

        return user
