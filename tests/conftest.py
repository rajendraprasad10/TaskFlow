import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base

TEST_DATABASE_URL = "sqlite://"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={
        "check_same_thread": False,
    },
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


@pytest.fixture
def db_session():

    Base.metadata.create_all(
        bind=engine
    )

    db = TestingSessionLocal()

    try:
        yield db
    finally:
        db.close()

        Base.metadata.drop_all(
            bind=engine
        )