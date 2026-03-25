from typing import Any
from sqlalchemy.ext.asyncio import AsyncSession


class UnitOfWork:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def commit(self):
        await self.session.commit()

    async def refresh(self, obj: Any):
        await self.session.refresh(obj)

    async def rollback(self):
        await self.session.rollback()
