# Smart Queue OCR API

Smart Queue OCR API is a lightweight, scalable, and asynchronous OCR (Optical Character Recognition) service built with FastAPI and asyncio. It supports image uploads, background OCR processing, job status querying, and advanced scalability via multiple parallel workers.

---

## 🚀 Main Features

- Upload images through REST API (`POST /images`).
- Asynchronous OCR processing with multiple parallel workers.
- Retrieve OCR results and job status (`GET /images/{job_id}`).
- Dedicated AI health check endpoint (`GET /health/ai`).
- Horizontal scaling with multiple workers.
- Dead-letter queue handling for failed jobs.
- Structured JSON logging for production readiness.

---

## ⚙️ Technologies Used

- **FastAPI** — High-performance web framework.
- **Uvicorn** — ASGI server.
- **asyncio.Queue** — For background task management.
- **RapidOCR** or **EasyOCR** — OCR engines.
- **SQLite** — Lightweight database for development.
- **Docker** — Containerization.
- **Docker Compose** — Local environment orchestration.

---

## 🛠️ Local Installation (Without Docker)

```bash
git clone https://github.com/youruser/smart-queue-ocr.git
cd smart-queue-ocr

python3 -m venv venv
source venv/bin/activate

pip install --upgrade pip
pip install -r requirements.txt

MAX_WORKERS=3 uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
```

The API will be available at `http://localhost:8000`

---

## 🐳 Installation via Docker Compose

```bash
docker-compose up --build
```

Access the service:

- API: `http://0.0.0.0:8000`

---

## 📚 Main Endpoints

| Method | Endpoint | Description |
|:------:|:---------|:------------|
| `POST` | `/images` | Upload an image for OCR processing |
| `GET` | `/images/{job_id}` | Check job status and OCR result |
| `GET` | `/health/ai` | Health check for the AI subsystem |

---

## 💡 Environment Variables

| Variable | Description | Default |
|:---------|:------------|:--------|
| `MAX_WORKERS` | Number of OCR workers | `1` |

---

## 🎯 Example Usage

**Uploading an image:**

You can use POSTMAN TO TEST API

```bash
curl -X POST "http://0.0.0.0:8000/images" -F "file=@path/to/your/image.jpg"
```

**Checking job status:**

```bash
curl "http://0.0.0.0:8000/images/{job_id}"
```

---

## 🔄 Worker Scaling

You can control the number of parallel OCR workers using the MAX_WORKERS environment variable (configured in the Docker Compose file or via the command line).
```bash
MAX_WORKERS=5 docker-compose up --build
```

Workers will process images concurrently, increasing throughput.

---

## 🌍 Project Structure

```
smart-queue-ocr/
|
|├ api/
|  └ main.py          # FastAPI entrypoint
|
|├ db/
|  ├ database.py       # Database connection setup
|  ├ crud.py           # CRUD operations
|  └ models.py         # ORM models
|
|├ worker/
|  └ processor.py      # OCR processing worker
|├ samples/
|  └ sample1.jpg
|  └ sample2.png
|├ Dockerfile
|├ docker-compose.yml
|├ requirements.txt
|└ README.md
```

---

## ✅ Current Features Implemented

- [x] Asynchronous image uploads
- [x] OCR job queue management
- [x] Parallel workers
- [x] Dead-letter queue handling
- [x] AI health check with confidence evaluation
- [x] JSON structured logging
- [x] Docker and Docker Compose support

---

## 📊 Possible Improvements

- **Dockerfile Multistage Optimization**:
  - Further optimize the final image size by installing only runtime dependencies.
  - Build wheels and binaries in the builder stage.

- **Database Enhancement**:
  - Replace SQLite with PostgreSQL for better parallelism and production-level scaling.

- **ONNX-only OCR Model**:
  - Switch to an ONNX-based OCR engine.
  - Enables packaging into a lightweight Python Alpine image.
  - Would significantly reduce Docker image size and RAM usage.

- **Monitoring and Observability**:
  - Add Prometheus metrics for queue length, processing time, and OCR success rates.

- **Authentication and Authorization**:
  - Add API Key validation for upload and retrieval endpoints.

- **Health Check Enhancements**:
  - Dynamically assess latency and system load with categorized AI quality outputs (good/acceptable/low).

---

