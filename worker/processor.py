# smart-queue-ocr/worker/processor.py
import asyncio
import time
from easyocr import Reader
from db.crud import get_job, update_job
import logging

logger = logging.getLogger(__name__) 
queue = asyncio.Queue()
reader = Reader(['en'], gpu=False)

async def ocr_worker():
    logger.info("[Worker] Starting OCR worker with thread id: %s", id(asyncio.current_task()))
    MAX_RETRIES = 3
    while True:
        job_id = await queue.get()
        job = await get_job(job_id)
        if not job:
            queue.task_done()
            continue

        for attempt in range(1, MAX_RETRIES + 1):
            try:
                if attempt == 1:
                    await update_job(
                        job_id,
                        status="processing",
                        text="",
                        confidence=0.0,
                        processing_time=0.0
                    )

                start_time = time.time()
                results = reader.readtext(job.path, detail=1)
                end_time = time.time()
                processing_time = end_time - start_time

                text = " ".join([res[1] for res in results])
                confidence = sum([res[2] for res in results]) / len(results) if results else 0.0

                await update_job(
                    job_id,
                    status="done",
                    text=text,
                    confidence=confidence,
                    processing_time=processing_time
                )

                logger.info(f"[Worker] Job {job_id} succeeded after {attempt} attempt(s) 🚀")
                break
            except Exception as e:
                if attempt == MAX_RETRIES:
                    await update_job(
                        job_id,
                        status=f"dead-letter: {str(e)}",
                        text="",
                        confidence=0.0,
                        processing_time=0.0
                    )
                    logger.error(f"[Worker] Job {job_id} failed after {MAX_RETRIES} attempts ❌ Error: {e}")
                else:
                    await asyncio.sleep(1)

        queue.task_done()

