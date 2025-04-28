# api/main.py
from fastapi import FastAPI, UploadFile, File, HTTPException, Request
from pydantic import BaseModel
from uuid import uuid4
import shutil
import os
import asyncio
from contextlib import asynccontextmanager

from slowapi.middleware import SlowAPIMiddleware
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi.responses import JSONResponse

from db.database import init_db
from db.crud import create_job, get_job
from worker.processor import queue, ocr_worker

import logging
from pythonjsonlogger import jsonlogger

from rapidocr_onnxruntime import RapidOCR
import time

ocr_benchmark = RapidOCR()
logger = logging.getLogger()
logHandler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter(
    '%(asctime)s %(levelname)s %(message)s'
)
logHandler.setFormatter(formatter)
logger.addHandler(logHandler)
logger.setLevel(logging.INFO)
num_workers = int(os.getenv("MAX_WORKERS", 1))

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info({"event": "startup", "message": "Application starting..."})
    await init_db()
    for _ in range(num_workers):
        asyncio.create_task(ocr_worker())
    yield
app = FastAPI(lifespan=lifespan)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
MIME_TYPE_TO_EXTENSION = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
    "image/bmp": ".bmp",
    "image/tiff": ".tiff",
}

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)
@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info({
        "event": "request_start",
        "method": request.method,
        "path": request.url.path
    })
    response = await call_next(request)
    logger.info({
        "event": "request_end",
        "method": request.method,
        "path": request.url.path,
        "status_code": response.status_code
    })
    return response

@app.exception_handler(RateLimitExceeded)
async def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded):
    return JSONResponse(
        status_code=429,
        content={"detail": "Rate limit exceeded"}
    )

class OCRResult(BaseModel):
    id: str
    status: str
    timestamp: str
    text: str
    confidence: float
    processing_time: float

@app.post("/images")
@limiter.limit("100/minute")
async def upload_image(request: Request, file: UploadFile = File(...)):

    extension = MIME_TYPE_TO_EXTENSION.get(file.content_type)

    if not extension:
        raise HTTPException(status_code=400, detail="Unsupported image type")

    job_id = str(uuid4())
    filename = f"{job_id}{extension}"
    file_path = os.path.join(UPLOAD_FOLDER, filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    await create_job(job_id, path=file_path)
    await queue.put(job_id)

    return {"id": job_id, "status": "queued"}

@app.get("/images/{job_id}", response_model=OCRResult)
@limiter.limit("100/minute")
async def get_result(request: Request, job_id: str):
    job = await get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    result = OCRResult(
        id=job.id,
        status=job.status,
        timestamp=job.timestamp.isoformat(),
        text=job.text,
        confidence=job.confidence,
        processing_time=job.processing_time
    )

    if job.status in ("queued", "processing"):
        return JSONResponse(
            status_code=202,
            content=result.dict()
        )
    else:
        return JSONResponse(
            status_code=200,
            content=result.dict()
        )

@app.get("/health/ai")
@limiter.limit("100/minute")
async def health_ai(request: Request):
    start_time = time.time()
    
    try:
        results, confidences = ocr_benchmark("samples/sample_health_check.jpg")
        
        latency = time.time() - start_time
        
        texts = []
        if isinstance(results, list):
            for item in results:
                if isinstance(item, list) and len(item) >= 2:
                    texts.append(item[1])
        text_summary = " ".join(texts)

        safe_confidences = [
            min(max(float(c), 0.0), 1.0)
            for c in confidences
            if isinstance(c, (int, float))
        ]

        avg_confidence = sum(safe_confidences) / len(safe_confidences) if safe_confidences else 0.0

        return {
            "status": "ok",
            "latency_seconds": latency,
            "sample_text": text_summary,
            "average_confidence": avg_confidence
        }
    except Exception as e:
        latency = time.time() - start_time
        return {
            "status": "error",
            "latency_seconds": latency,
            "detail": str(e)
        }


