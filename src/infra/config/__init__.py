import dotenv
from dataclasses import dataclass
from pydantic import BaseModel


class DBConfig(BaseModel):
    """Database configuration."""

    host: str
    port: int
    engine: str
    username: str
    password: str
    database_name: str


class Config(BaseModel):
    """Configuration class for the application."""

    db: DBConfig


def _load_config() -> Config:
    """
    Load environment variables from a .env file.
    """
    dotenv.load_dotenv(".env")

    return Config(
        db=DBConfig(
            host=dotenv.get_key(".env", "DB_HOST"),
            port=int(dotenv.get_key(".env", "DB_PORT")),
            engine=dotenv.get_key(".env", "DB_ENGINE"),
            username=dotenv.get_key(".env", "DB_USERNAME"),
            password=dotenv.get_key(".env", "DB_PASSWORD"),
            database_name=dotenv.get_key(".env", "DB_DATABASE_NAME"),
        ),
    )


config = _load_config()
