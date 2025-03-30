from datetime import datetime
from sqlmodel import Session

from src.gh.models import Event


def prepare_data(session: Session):
    for repo_id in [1, 2]:
        for event_id in range(7):
            repo = f"org/repo{repo_id}"
            time = f"0{event_id}:00:00"
            event = Event(
                event_id=event_id,
                type="PushEvent",
                createted_at=datetime.fromisoformat(f"2025-03-28T{time}-00:00"),
                repo=repo,
                repo_id=repo_id,
                actor_id=1,
            )
            session.add(event)
    event = Event(
        event_id=10,
        type="WatchEvent",
        createted_at=datetime.fromisoformat("2025-03-28T12:00:00-00:00"),
        repo="org/repo1",
        repo_id=1,
        actor_id=1,
    )
    session.add(event)
    session.commit()
