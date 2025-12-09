# Docker Setup Guide

## Overview
This project is now fully dockerized with both frontend and backend services, plus a Chroma vector database service.

## Services

### Backend
- **Port**: 8000
- **Image**: Python 3.11 with FastAPI
- **Entry Point**: Gunicorn + Uvicorn workers

### Frontend
- **Port**: 5000
- **Image**: Node 20 Alpine with React/Vite
- **Entry Point**: Serve static files

### Chroma (Vector Database)
- **Port**: 8001 (mapped from 8000 inside container)
- **Image**: Official Chroma Docker image

## Prerequisites

1. **Docker**: [Install Docker Desktop](https://www.docker.com/products/docker-desktop)
2. **Docker Compose**: Usually comes with Docker Desktop

## Quick Start

### Build and Start All Services

```bash
# Navigate to project root
cd Research-Application-CAG

# Build images and start services
docker-compose up --build

# Or run in background
docker-compose up -d --build
```

### Stop Services

```bash
docker-compose down

# To also remove volumes
docker-compose down -v
```

## Individual Commands

### Build Images

```bash
# Build all services
docker-compose build

# Rebuild without cache
docker-compose build --no-cache
```

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f chroma
```

### Access Services

- **Frontend**: http://localhost:5000
- **Backend API**: http://localhost:8000
- **Backend Docs**: http://localhost:8000/docs
- **Chroma API**: http://localhost:8001/api/v1

## Environment Variables

### Frontend
- `VITE_API_URL`: Backend API URL (default: `http://backend:8000` in Docker)

### Backend
- `PYTHONUNBUFFERED`: Set to 1 for unbuffered output

## Building Images Manually

### Frontend Only
```bash
cd frontend
docker build -t research-app-frontend:latest .
cd ..
```

### Backend Only
```bash
cd backend
docker build -t research-app-backend:latest .
cd ..
```

## Production Considerations

1. **CORS**: Update `allow_origins` in `backend/main.py` with your domain
2. **Environment Variables**: Use `.env` files for sensitive data
3. **Volumes**: Chroma data persists in the `chroma-data` volume
4. **Health Checks**: All services have health checks configured
5. **Networking**: Services communicate via `research-network` bridge network

## Troubleshooting

### Port Already in Use
```bash
# Kill process on specific port (Windows)
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

### Rebuild Everything
```bash
docker-compose down -v
docker-compose build --no-cache
docker-compose up
```

### View Container Status
```bash
docker-compose ps
```

### Execute Commands in Container
```bash
# Backend shell
docker-compose exec backend bash

# Frontend shell
docker-compose exec frontend sh
```

## Development Mode

For hot-reload during development, modify `docker-compose.yml` to mount source directories as volumes. The `backend` service already has this configured.

## Notes

- Frontend uses Alpine Linux for smaller image size
- Backend uses Python slim image for optimization
- Both use multi-stage builds for smaller final images
- All services are on the same Docker network for easy inter-service communication
