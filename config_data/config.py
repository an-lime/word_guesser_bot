from dataclasses import dataclass

from environs import Env


@dataclass
class TgBot:
    token: str


@dataclass
class Db:
    LOGIN: str
    PASSWORD: str
    HOST: str
    PORT: str
    DB: str

    def __post_init__(self):
        self.url = f'postgresql+asyncpg://{self.LOGIN}:{self.PASSWORD}@{self.HOST}:{self.PORT}/{self.DB}'


@dataclass
class BotConfig:
    tgBot: TgBot
    db: Db


def load_config(path: str | None = None) -> BotConfig:
    env = Env()
    env.read_env(path)
    config: BotConfig = BotConfig(
        tgBot=TgBot(token=env('BOT_TOKEN')),
        db=Db(LOGIN=env('DB_LOGIN'), PASSWORD=env('DB_PASSWORD'), HOST=env('DB_HOST'), PORT=env('DB_PORT'),
              DB=env('DB')))

    return config
