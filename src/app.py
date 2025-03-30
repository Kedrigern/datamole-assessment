from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from sqlmodel import Session

from src.config import config
from src.database.connection import get_session
from src.gh.models import Event
from src.gh.event import fetch_gh_to_local_db
from src.stats.event import get_stats, fetch_repos


@asynccontextmanager
async def life_span(_: FastAPI):
    yield


app = FastAPI(
    title=config.app_name,
    description="A REST API for localy cached GH stats.",
    lifespan=life_span,
)


@app.get("/")
def home(session: Session = Depends(get_session)):
    result = {
        "info": f"Hello world from {config.app_name}!",
        "example_paths": [
            "/",
            "stats/{org}/{repo}/{event_type}",
            "/fetch",
            "/docs",
            "/redoc",
        ],
        "repos_configured": config.repos,
        "repos_cached": fetch_repos(session),
    }
    return result


@app.get("/stats/{org}/{repo}/{type}")
def stats(
    org: str, repo: str, type: str, session: Session = Depends(get_session)
) -> dict:
    """
    Returns the average time difference between consecutive events of the given type in the repository
    Type: PushEvent | WatchEvent | ...
    """
    repo_uri: str = org + "/" + repo
    td, events_count = get_stats(session, repo_uri, type)
    if not td:
        return {"repo": repo_uri, "type": type, "error": "error"}
    return {
        "repo": repo_uri,
        "type": type,
        "avg_time_diff": td.seconds,
        "avg_time_diff_unit": "seconds",
        "avg_time_diff_str": str(td),
        "events_count": events_count,
    }


@app.get("/fetch")
def fetch_gh_from_config(session: Session = Depends(get_session)):
    result: dict[str, list[Event]] = fetch_gh_to_local_db(session)
    return result


@app.get("/fetch/{org}/{repo}")
def fetch_gh(org: str, repo: str, session: Session = Depends(get_session)) -> dict:
    repo_uri: str = org + "/" + repo
    result: dict[str, list[Event]] = fetch_gh_to_local_db(session, repo_uri)
    return result
