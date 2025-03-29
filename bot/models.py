from typing import Self

from sqlalchemy import BigInteger, select
from sqlalchemy.ext.asyncio import AsyncAttrs, AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

type BigInt = int


class Base(AsyncAttrs, DeclarativeBase):
    type_annotation_map = {
        BigInt: BigInteger,
    }


class Member(Base):
    __tablename__ = "members"

    id: Mapped[BigInt] = mapped_column(primary_key=True, autoincrement=False)
    dm_sent: Mapped[bool] = mapped_column(default=False, nullable=False)
    reacted: Mapped[bool] = mapped_column(default=False, nullable=False)

    @classmethod
    async def get_by_id(cls, id: int, *, session: AsyncSession) -> Self | None:
        stmt = select(cls).filter(cls.id == id)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    @classmethod
    async def get_or_create(cls, id: int, *, session: AsyncSession) -> tuple[Self, bool]:
        instance = await cls.get_by_id(id, session=session)
        if instance is not None:
            return instance, False

        new_instance = cls(id=id)
        session.add(new_instance)
        await session.flush()
        await session.refresh(new_instance)
        return new_instance, True
