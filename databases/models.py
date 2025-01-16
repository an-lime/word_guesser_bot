from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql.expression import func, select, delete

from databases.base import Base


class Users(Base):
    __tablename__ = 'users'

    id_user: Mapped[str] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(nullable=False)
    win_points: Mapped[int] = mapped_column(nullable=False, default=0)

    async def add_user(self, id_user: str, name: str, session: AsyncSession) -> None:
        user = await session.get(Users, id_user)
        if not user:
            user = Users(id_user=id_user, name=name)
            session.add(user)
        await session.commit()


class Words(Base):
    __tablename__ = 'words'
    id_word: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    word: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[str] = mapped_column(nullable=False)

    async def get_random_word(self, session: AsyncSession):
        statement = select(Words).order_by(func.random()).limit(1)
        result = await session.execute(statement)
        words = result.scalars().all()
        return words[0]


class UserInGame(Base):
    __tablename__ = 'user_in_game'
    id_game: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    id_user: Mapped[str] = mapped_column(primary_key=True)
    id_word: Mapped[int] = mapped_column(primary_key=True)

    async def add_game(self, id_user: str, id_word: int, session: AsyncSession) -> None:
        user_in_game = UserInGame(id_user=id_user, id_word=id_word)
        session.add(user_in_game)
        await session.commit()

    async def stop_game(self, id_user: str, session: AsyncSession) -> None:
        statement = delete(UserInGame).where(UserInGame.id_user == id_user)
        await session.execute(statement)
        await session.commit()