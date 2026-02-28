from sqlalchemy import create_engine, Column, String, Integer, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime

DATABASE_URL = "sqlite:///./aramco_ai.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Ticket(Base):
    __tablename__ = "tickets"
    ticket_id = Column(String, primary_key=True)
    caller_id = Column(String)
    issue_type = Column(String)
    urgency = Column(String)
    description = Column(Text)
    status = Column(String, default="Open")
    created_at = Column(DateTime, default=datetime.datetime.now)
    scheduled_time = Column(DateTime, nullable=True)

class CallLog(Base):
    __tablename__ = "call_logs"
    id = Column(Integer, primary_key=True)
    caller_id = Column(String)
    transcript = Column(Text)
    sentiment = Column(String)
    summary = Column(Text)
    timestamp = Column(DateTime, default=datetime.datetime.now)
    language = Column(String, default="en")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_db_and_tables():
    Base.metadata.create_all(engine)
    print("✅ SQLite Ready!")
