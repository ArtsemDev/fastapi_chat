from datetime import datetime

from sqlalchemy import Column, VARCHAR, INT, ForeignKey, TIMESTAMP
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from .settings import SETTINGS


class Base(DeclarativeBase):
    _engine = create_async_engine(SETTINGS.DATABASE_URL.replace('postgresql://', 'postgresql+asyncpg://'))
    session = async_sessionmaker(bind=_engine)


class User(Base):
    __tablename__ = 'user'

    id = Column(INT, primary_key=True)
    email = Column(VARCHAR(128), nullable=False, unique=True)
    password = Column(VARCHAR(256), nullable=False)


class ChatMessage(Base):
    __tablename__ = 'chat_message'

    id = Column(INT, primary_key=True)
    chat_id = Column(INT, ForeignKey('chat.id', ondelete='CASCADE'), nullable=False)
    message = Column(VARCHAR(1024), nullable=False)
    author_id = Column(INT, ForeignKey('user.id', ondelete='NO ACTION'), nullable=False)
    date_created = Column(TIMESTAMP, default=datetime.utcnow())


class Chat(Base):
    __tablename__ = 'chat'

    id = Column(INT, primary_key=True)

