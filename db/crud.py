# smart-queue-ocr/db/crud.py
from sqlalchemy.future import select
from sqlalchemy import update as sql_update
from db.models import OCRJob
from db.database import async_session
from datetime import datetime

async def create_job(id: str, path: str):
    async with async_session() as session:
        job = OCRJob(
            id=id,
            status="queued",
            path=path
        )
        session.add(job)
        await session.commit()
        return job

async def get_job(id: str):
    async with async_session() as session:
        result = await session.execute(select(OCRJob).where(OCRJob.id == id))
        return result.scalar_one_or_none()

async def update_job(id: str, status: str, text: str, confidence: float, processing_time: float):
    async with async_session() as session:
        await session.execute(
            sql_update(OCRJob)
            .where(OCRJob.id == id)
            .values(
                status=status,
                text=text,
                confidence=confidence,
                processing_time=processing_time,
                timestamp=datetime.utcnow()
            )
        )
        await session.commit()
