"""Engine/session factory. `DATABASE_URL` switches Neon Postgres ↔ SQLite with the same models."""
from __future__ import annotations

from pathlib import Path

from sqlalchemy import create_engine, event, select, text
from sqlalchemy.engine import Engine, make_url
from sqlalchemy.orm import Session, sessionmaker

from .config import BACKEND_DIR
from .models import AppUser, Base
from .seed_data import DEFAULT_ADM4, DEMO_USER_ID, DEMO_USER_NAME


def normalize_url(url: str) -> str:
    """Accept the URL as Neon prints it (postgresql://…?sslmode=require) and use psycopg 3."""
    if url.startswith("postgres://"):
        url = "postgresql://" + url[len("postgres://"):]
    if url.startswith("postgresql://"):
        url = "postgresql+psycopg://" + url[len("postgresql://"):]
    if url.startswith("sqlite:///") and not url.startswith("sqlite:////") and url != "sqlite:///:memory:":
        p = Path(url[len("sqlite:///"):])
        if not p.is_absolute():  # relative SQLite paths resolve against backend/, not the CWD
            url = "sqlite:///" + (BACKEND_DIR / p).as_posix()
    return url


def backend_name(url: str) -> str:
    u = make_url(normalize_url(url))
    if u.get_backend_name() == "sqlite":
        return "sqlite"
    return "neon" if u.host and "neon.tech" in u.host else "postgresql"


def make_engine(url: str) -> Engine:
    url = normalize_url(url)
    if url.startswith("sqlite"):
        engine = create_engine(url, connect_args={"check_same_thread": False, "timeout": 15})

        @event.listens_for(engine, "connect")
        def _sqlite_pragmas(dbapi_conn, _):  # FK + CHECK enforcement like Postgres
            cur = dbapi_conn.cursor()
            cur.execute("PRAGMA foreign_keys=ON")
            cur.execute("PRAGMA journal_mode=WAL")
            cur.close()

        return engine
    # pool_pre_ping: survive laptop sleep / Neon scale-to-zero dropping idle connections.
    # prepare_threshold=None: no server-side prepared statements, safe behind Neon's PgBouncer pooler.
    return create_engine(url, pool_pre_ping=True, pool_size=5, max_overflow=5,
                         connect_args={"prepare_threshold": None})


def make_sessionmaker(engine: Engine) -> sessionmaker[Session]:
    return sessionmaker(engine, expire_on_commit=False)


def init_db(engine: Engine) -> None:
    Base.metadata.create_all(engine)
    with Session(engine) as s:
        if s.get(AppUser, DEMO_USER_ID) is None:
            s.add(AppUser(id=DEMO_USER_ID, display_name=DEMO_USER_NAME, gender="female", home_adm4=DEFAULT_ADM4))
            s.commit()


def ping(engine: Engine) -> None:
    with engine.connect() as c:
        c.execute(text("SELECT 1"))


def count(session: Session, model) -> int:
    from sqlalchemy import func

    return session.scalar(select(func.count()).select_from(model)) or 0
