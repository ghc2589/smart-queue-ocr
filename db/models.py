# db/models.py
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy import String, Float, DateTime
from datetime import datetime

class Base(AsyncAttrs, DeclarativeBase):
    pass

class OCRJob(Base):
    __tablename__ = "ocr_jobs"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    status: Mapped[str] = mapped_column(String)
    timestamp: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    text: Mapped[str] = mapped_column(String, default="")
    confidence: Mapped[float] = mapped_column(Float, default=0.0)
    path: Mapped[str] = mapped_column(String)
    processing_time: Mapped[float] = mapped_column(Float, default=0.0)
