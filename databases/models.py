from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql.expression import func, select, delete

from databases.base import Base


class Users(Base):
    __tablename__ = 'users'

    id_user: Mapped[str] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(nullable=False)
    win_points: Mapped[int] = mapped_column(nullable=False, default=0)

    async def add_user(self, id_user: str, name: str, session: AsyncSession) -> None:
        user = await session.get(Users, id_user)
        if not user:
            user = Users(id_user=id_user, name=name)
            session.add(user)
        await session.commit()

    async def update_user(self, id_user: str, points: int, session: AsyncSession) -> None:
        user = await session.get(Users, id_user)
        if user and points is not None:
            user.win_points += points
        await session.commit()

    async def show_users(self, id_user: str, session: AsyncSession) -> str:
        user_place: str = 'Твоё место -- '

        final_list: str = 'Таблица лидеров:\n\n'
        statement = select(
            func.row_number().over(order_by=Users.win_points.desc()), Users.id_user, Users.name,
            Users.win_points).order_by(
            Users.win_points.desc())

        result = await session.execute(statement)
        users = result.all()
        for user in users:

            if user[1] == id_user:
                user_place += f'{str(user[0])} (Количество очков: {str(user[3])})\n\n'

            if user[0] <= 10:
                row_number = user[0]
                model_user: Users = Users(name=user[2], win_points=user[3])

                match row_number:
                    case 1:
                        medal = '🥇'
                    case 2:
                        medal = '🥈'
                    case 3:
                        medal = '🥉'
                    case _:
                        medal = '🏅'

                final_list += f'{medal} {row_number}. {model_user.name}: (Очки: {model_user.win_points})\n\n'

        await session.commit()

        final_list = f'{user_place}\n{final_list}'

        return final_list


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
