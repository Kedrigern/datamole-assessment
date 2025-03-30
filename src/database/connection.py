from typing import Iterator
from sqlmodel import SQLModel, Session, create_engine
from src.config import config

connect_args = {"check_same_thread": False}
engine = create_engine(
    f"sqlite:///{config.events_db}.db?mode=ro", echo=True, connect_args=connect_args
)


def create_db_and_tables() -> None:
    SQLModel.metadata.create_all(engine)


def get_session() -> Iterator[Session]:
    with Session(engine) as session:
        yield session
