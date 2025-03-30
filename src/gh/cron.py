from datetime import datetime
from sqlmodel import Session

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

from src.config import config
from src.database.connection import get_session
from src.gh.event import fetch_gh_to_local_db


def create_scheduler():
    scheduler = BackgroundScheduler()
    trigger = IntervalTrigger(
        minutes=config.auto_fetch_interval_minutes, start_date=datetime.now()
    )

    def cron_fetch(session: Session):
        print("--- CRON JOB ---")
        fetch_gh_to_local_db(session)

    session: Session = get_session()
    scheduler.add_job(cron_fetch, trigger, session)
    scheduler.start()
