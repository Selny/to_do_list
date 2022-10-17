from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.sql import func

Base = declarative_base()

class Task(Base):

    __tablename__ = 'Task'

    id = Column(Integer, primary_key = True)
    title = Column(String(45), nullable = False)
    rank = Column(Integer)
    done = Column(Boolean, nullable = False, default=False)
    Time = Column(DateTime(timezone=True), nullable=False, default = func.now())
    user_id = Column(Integer, nullable = False)

class User(Base):

    __tablename__ = 'User'

    id = Column(Integer, primary_key = True)
    username = Column(String(16), nullable = False)
    password = Column(String(64), nullable = False)