from sqlalchemy.future import select
from sqlalchemy import insert
from sqlalchemy.orm import aliased
from .models import *

from datetime import datetime


async def get_projects(ip_address):
    async with async_session() as session:
        q = (
            select(Project)
            .join(user_project,
                  Project.id == user_project.c.project_id)
            .join(User, User.id == user_project.c.user_id)
            .where(User.ip_address == ip_address)
        )

        result = await session.execute(q)
        projects = result.scalars().all()

    return projects


async def create_project(ip_address, name):
    async with async_session() as session:
        project = Project(name=name, datetime=datetime.now())
        session.add(project)
        await session.flush()

        q = select(User).where(User.ip_address == ip_address)
        result = await session.execute(q)
        user = result.scalar()
        if user is None:
            user = User(ip_address=ip_address)
            session.add(user)
            await session.flush()

        project_id = project.id
        stmt = insert(user_project).values(
            user_id=user.id, project_id=project_id)
        await session.execute(stmt)
        await session.commit()

        return project_id


async def set_cover_project(project_id, cover):
    async with async_session() as session:
        q = select(Project).where(Project.id == project_id)
        result = await session.execute(q)
        project = result.scalar()
        project.cover = cover
        await session.commit()


async def get_clips_id(project_id):
    async with async_session() as session:
        q = select(Clip.id).where(Clip.project_id == project_id)
        result = await session.execute(q)
        clips_id = result.scalars().all()

    return clips_id


async def get_clip_details(clip_id):
    async with async_session() as session:
        q = select(Clip.cover, Clip.title, Clip.duration).where(
            Clip.id == clip_id)
        result = await session.execute(q)
        clip = result.one()

    return clip


async def get_clip(clip_id):
    async with async_session() as session:
        q = select(Clip).where(
            Clip.id == clip_id)
        result = await session.execute(q)
        clip = result.one()

    return clip


async def update_clip(clip_id, subtitle, adhd):
    async with async_session() as session:
        q = select(Clip).where(Clip.id == clip_id)
        result = await session.execute(q)
        clip = result.scalar()
        clip.subtitle = subtitle
        clip.adhd = adhd
        await session.commit()


async def delete_clip(clip_id):
    async with async_session() as session:
        q = select(Clip).where(Clip.id == clip_id)
        result = await session.execute(q)
        clip = result.scalar()
        session.delete(clip)
        await session.commit()


async def create_clip(project_id, title, duration, cover, tags="", subtitles="", start=None, end=None, subtitle=True, adhd=False):
    async with async_session() as session:
        clip = Clip(project_id=project_id, title=title, duration=duration, cover=cover,
                    tags=tags, subtitles=subtitles, start=start, end=end, subtitle=subtitle, adhd=adhd)
        session.add(clip)
        await session.flush()
        clip_id = clip.id
        await session.commit()

        return clip_id
