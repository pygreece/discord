from typing import Self

from sqlalchemy import select
from sqlalchemy.ext.asyncio import (
    AsyncAttrs,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from bot import config

engine = create_async_engine(config.DATABASE_URL)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(AsyncAttrs, DeclarativeBase):
    pass


class Member(Base):
    __tablename__ = "members"

    id: Mapped[int] = mapped_column(primary_key=True)
    dm_sent: Mapped[bool] = mapped_column(default=False, nullable=False)
    reacted: Mapped[bool] = mapped_column(default=False, nullable=False)

    @classmethod
    async def filter_by_id(cls, id: int) -> Self | None:
        async with async_session() as session:
            stmt = select(cls).filter(cls.id == id)
            result = await session.execute(stmt)
            return result.scalar_one_or_none()

    @classmethod
    async def get_or_create(cls, id: int) -> tuple[Self, bool]:
        async with async_session() as session:
            stmt = select(cls).filter(cls.id == id)
            result = await session.execute(stmt)
            instance = result.scalar_one_or_none()
            if instance is not None:
                return instance, False

            new_instance = cls(id=id)
            session.add(new_instance)
            await session.commit()
            return new_instance, True

    async def save(self) -> None:
        async with async_session() as session:
            session.add(self)
            await session.commit()
