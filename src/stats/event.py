from datetime import datetime, timezone, timedelta
from sqlmodel import Session
from sqlalchemy import text


def fetch_repos(session: Session) -> list[str]:
    query = text("SELECT distinct(repo) FROM event;")
    results = session.connection().execute(query).fetchall()
    return [row[0] for row in results]


def fetch_events(
    session: Session, repo: str, event_type: str, first_date: datetime | None = None
) -> list[datetime]:
    """
    Returns a list of datetime objects representing event creation times,
    with their timezone explicitly set to UTC.

    This function retrieves events for a specific repository and event type
    that occurred within the last 7 days up to the specified 'first_date'
    (or the current time if not provided). The number of events returned
    is limited to a maximum of 500, ordered by their creation time.

    Be aware that SQLite does not have built-in timezone support.
    This function assumes that the 'createted_at' values in the database
    are intended to represent times in UTC.
    """
    query = text(
        """
    SELECT createted_at 
    FROM event 
    WHERE repo = :repo AND 
    type = :type AND 
    createted_at < :first_date AND
    createted_at > :last_date
    ORDER BY createted_at LIMIT 500;
    """
    )

    if not first_date:
        first_date = datetime.now(timezone.utc)

    last_date: datetime = first_date - timedelta(days=7)

    results = (
        session.connection()
        .execute(
            query,
            {
                "repo": repo,
                "type": event_type,
                "first_date": first_date,
                "last_date": last_date,
            },
        )
        .fetchall()
    )

    for row in results:
        print(row)
    timestamps = [
        datetime.fromisoformat(row[0].replace("Z", "+00:00")).replace(
            tzinfo=timezone.utc
        )
        for row in results
    ]

    return timestamps


def calculate_avg_time_difference(timestamps: list[datetime]) -> timedelta | None:
    """
    Calculates the average time difference between consecutive events
    in a list of timestamps.

    Args:
        timestamps: A sorted list of datetime objects.

    Returns:
        The average time difference as a timedelta object, or None
        if the list is empty or contains fewer than two events.
    """
    if len(timestamps) < 2:
        return None

    time_differences: list[timedelta] = []
    for i in range(len(timestamps) - 1):
        time_diff = timestamps[i + 1] - timestamps[i]
        time_differences.append(time_diff)

    if not time_differences:
        return None

    total_seconds = sum(td.total_seconds() for td in time_differences)
    average_seconds = total_seconds / len(time_differences)
    return timedelta(seconds=average_seconds)


def get_stats(
    session: Session, repo: str, event_type: str, first_date: datetime | None = None
) -> tuple[timedelta | None, int]:
    timestamps = fetch_events(session, repo, event_type, first_date)
    td = calculate_avg_time_difference(timestamps)
    return (td, len(timestamps))
