import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

# echo=True logs every SQL statement to console — useful while developing,
# turn off (or make conditional on an env var) once things stabilize
engine = create_engine(DATABASE_URL, echo=True)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """
    FastAPI dependency — provides a database session per request,
    and guarantees it's closed afterward even if an error occurs.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()