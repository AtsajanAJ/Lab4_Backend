# Backend

This repository contains the backend source code (FastAPI) and Dockerfile for building the backend Docker image.

## Files

- `main.py` - FastAPI application source code
- `requirements.txt` - Python dependencies
- `Dockerfile` - Docker configuration for building the backend container

## Dependencies

- FastAPI
- Redis
- Uvicorn

## Building Docker Image

To build the Docker image:

```bash
docker build -t backend-image .
```

## Running the Container

To run the container:

```bash
docker run -d -p 8000:8000 -e REDIS_HOST=redis backend-image
```

## API Endpoints

- `GET /` - Main counter page
- `GET /api/counter` - Get current counter value
- `POST /api/increment` - Increment counter
- `GET /health` - Health check endpoint
- `GET /reset` - Reset counter to zero
