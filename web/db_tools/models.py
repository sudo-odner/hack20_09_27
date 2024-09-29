import os
from dotenv import load_dotenv

import asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import (Boolean, Column, ForeignKey, Integer,
                        String, Table, LargeBinary, DateTime, event)

load_dotenv()

username = os.getenv('POSTGRES_USER')
password = os.getenv('POSTGRES_PASSWORD')
if os.getenv('DOCKER_CONTAINER'):
    host = os.getenv('DB_HOST')
else:
    host = '127.0.0.1'
database = os.getenv('POSTGRES_DB')
conn_url = f'postgresql+asyncpg://{username}:{password}@{host}:5432/{database}'

engine = create_async_engine(conn_url, echo=False)

async_session = sessionmaker(engine, class_=AsyncSession)

Base = declarative_base()


user_project = Table(
    'user_project',
    Base.metadata,
    Column('user_id', Integer,
           ForeignKey('user.id')),
    Column('project_id', Integer,
           ForeignKey('project.id'))
)


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    ip_address = Column(String, nullable=False)
    projects = relationship(
        'Project', secondary=user_project, back_populates='users')


class Project(Base):
    __tablename__ = 'project'

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    cover = Column(LargeBinary, nullable=True)
    datetime = Column(DateTime, nullable=False)
    token_model = Column(String, nullable=True)
    users = relationship(
        'User', secondary=user_project, back_populates='projects')


class Clip(Base):
    __tablename__ = 'clip'

    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey('project.id'))
    title = Column(String, nullable=False)
    about = Column(String, nullable=True)
    duration = Column(Integer, nullable=False)
    cover = Column(LargeBinary, nullable=True)
    tags = Column(String, nullable=True)
    subtitles = Column(String, nullable=True)
    start = Column(Integer, nullable=True)
    end = Column(Integer, nullable=True)
    subtitle = Column(Boolean, nullable=False)
    adhd = Column(Boolean, nullable=False)
