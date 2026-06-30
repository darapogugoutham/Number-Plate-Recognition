# Number Plate Recognition System

An end-to-end Automatic License Plate Recognition MVP built with Python, FastAPI, OpenCV, Tesseract OCR, and detection history storage.

## Features

- Upload `.jpg`, `.jpeg`, or `.png` vehicle images.
- Detect plate-like regions with an OpenCV contour baseline.
- Crop and enhance the plate region before OCR.
- Extract text with Tesseract and clean OCR noise.
- Store recognition history, crop paths, confidence scores, status, and processing time.
- Use local JSON history by default or MongoDB when `MONGODB_URL` is configured.
- Query detection history and basic metrics through REST APIs.
- Run locally or with Docker Compose.

## Architecture

```text
Image Upload -> Storage -> OpenCV Preprocessing -> Plate Detection -> Crop -> OCR -> Post-processing -> History API
```

## API Endpoints

| Method | Endpoint | Purpose |
| --- | --- | --- |
| `GET` | `/api/v1/health` | Health check |
| `GET` | `/api/v1/metrics` | Basic recognition metrics |
| `POST` | `/api/v1/recognize/image` | Upload and recognize an image |
| `GET` | `/api/v1/detections` | List detection history |
| `GET` | `/api/v1/detections/search?plate=ABC123` | Search by plate text |
| `GET` | `/api/v1/detections/{id}` | Fetch one detection |
| `DELETE` | `/api/v1/detections/{id}` | Delete one detection |

## Local Setup

Install system Tesseract first:

```bash
brew install tesseract
```

Create a virtual environment and install dependencies:

```bash
cd backend
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open the API docs at:

```text
http://127.0.0.1:8000/docs
```

## Docker

```bash
docker compose up --build
```

The backend runs at `http://127.0.0.1:8000`.

## Dashboard

After starting the backend, open `frontend/index.html` in your browser. It provides image upload, result preview, crop display, and detection history using the FastAPI endpoints.

The dashboard also includes a demo sample gallery. Click `Try` on one sample to generate a known vehicle image in the browser and upload it to the recognition API, or click `Run All` to compare the expected plate text against the recognized output across easy, angled, low-light, noisy, and no-plate cases.

## Testing

```bash
pytest
```

## Current Scope

This first version is intentionally an MVP. It uses OpenCV contour filtering for plate localization and Tesseract for OCR. That is enough for a portfolio-ready baseline and leaves a clean upgrade path to YOLO or TensorFlow Object Detection.

## Upgrade Roadmap

- Add a React dashboard for upload, result preview, and history search.
- Replace contour detection with a trained YOLO/TFOD plate detector.
- Add video frame sampling and duplicate plate tracking.
- Add evaluation scripts for detection precision, recall, OCR character accuracy, and latency.

## Privacy Notice

This project is intended for educational and portfolio use. Only process vehicle images when you have permission to handle the vehicle information.
