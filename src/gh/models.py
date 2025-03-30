from datetime import datetime
from sqlmodel import Field, SQLModel


class Event(SQLModel, table=True):
    """
    Serve as SQLModel and Pydantic model as well
    PK is combination of event_id and repo_id
    """

    event_id: int = Field(primary_key=True)
    type: str
    createted_at: datetime
    repo: str
    repo_id: int = Field(primary_key=True)
    actor_id: int

    def __str__(self):
        return f"Event<{self.type} {self.createted_at}>"

    def __repr__(self):
        return f"Event<{self.type} {self.createted_at}>"
