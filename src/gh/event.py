import sys
from datetime import datetime, timezone
import requests
import requests_cache
from requests.utils import parse_header_links
from sqlmodel import Session, select
from sqlalchemy.exc import IntegrityError
from .models import Event
from src.config import config


def next_page(link_header: str) -> str | None:
    """
    If there is a next page return valid url, otherwise return None
    """
    links = parse_header_links(link_header)
    for link in links:
        if link["rel"] == "next":
            return link["url"]
    return None


def proccess_page(url: str, events: list[Event], oldest_date: datetime) -> str | None:
    """
    Proccess one page from API
    Return next page (url) or None if there is no next page
    """
    response: requests.Response = requests.get(url)
    response.raise_for_status()

    print(url, oldest_date)

    for event in response.json():
        createted_at = datetime.fromisoformat(event["created_at"])
        if createted_at <= oldest_date:
            return None
        events.append(
            Event(
                event_id=event["id"],
                type=event["type"],
                createted_at=createted_at,
                repo=event["repo"]["name"],
                repo_id=event["repo"]["id"],
                actor_id=event["actor"]["id"],
            )
        )

    if "link" in response.headers:
        return next_page(response.headers["link"])
    else:
        return None


def fetch_repo(repo: str, last: Event = None) -> list[Event]:
    """
    Prepare list of events for repository
    Handle the pagination
    Returns list of events
    """
    url: str = config.base_url + repo + config.end_of_url
    events: list[Event] = []
    if last:
        oldest_date = last.createted_at.replace(tzinfo=timezone.utc)
    else:
        oldest_date = config.history_limit

    while url:
        url = proccess_page(url, events, oldest_date)

    return events


def save_to_db(session: Session, data: dict[str, list[Event]]) -> None:
    """
    Save events to database
    """
    for repo in data:
        for event in data[repo]:
            try:
                session.add(event)
            except IntegrityError:
                print(
                    f"Integrity error, new data are not saved to DB. {event.type} {event.createted_at}",
                    file=sys.stderr,
                )
        session.commit()


def proccess_repositories(
    session: Session, repos: list[str], result: dict[str, list[Event]]
) -> None:
    requests_cache.install_cache(
        config.requests_cache, expire_after=config.expire_after
    )
    for repo in repos:
        statement = (
            select(Event)
            .where(Event.repo == repo)
            .order_by(Event.createted_at.desc())
            .limit(1)
        )
        last: Event | None = session.exec(statement).first()
        try:
            events = fetch_repo(repo, last)
            result[repo] = events
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 403:
                print(f"[403] Repo {repo} rate limit exceeded.", file=sys.stderr)
            elif e.response.status_code == 404:
                print(f"[404] Repo {repo} does not exist.", file=sys.stderr)
            else:
                print(
                    f"[{e.response.status_code}] Repo {repo} failed: ",
                    e,
                    file=sys.stderr,
                )
            continue


def fetch_gh_to_local_db(session: Session, repo_uri=None) -> dict:
    result: dict[str, list[Event]] = {}
    if repo_uri:
        proccess_repositories(session, [repo_uri], result)
    else:
        proccess_repositories(session, config.repos, result)

    stats = {}
    for repo in result:
        stats[repo] = len(result[repo])

    save_to_db(session, result)
    return stats
