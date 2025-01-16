from sqlalchemy.ext.asyncio import AsyncSession

from databases.models import Users, Words, UserInGame


class Database:
    def __init__(self, session: AsyncSession, users: Users, words: Words, user_in_game: UserInGame):
        self.session = session
        self.users = users
        self.words = words
        self.user_in_game = user_in_game
