# ---------- builder ----------
FROM python:3.11-slim AS builder
WORKDIR /

# install build deps
RUN apt-get update && apt-get install -y build-essential gcc && rm -rf /var/lib/apt/lists/*

# copy deps and install into /opt/venv for smaller final image
COPY requirements.txt .
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --upgrade pip
RUN pip wheel --wheel-dir=/wheels -r requirements.txt

# ---------- runtime ----------
FROM python:3.11-slim
WORKDIR /

# create non-root user (recommended)
RUN useradd --create-home appuser
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# copy app code
COPY ./app /app/app

# expose port (uvicorn/gunicorn)
EXPOSE 8000

# run with Gunicorn + Uvicorn workers (production)
CMD ["gunicorn", "app.main:app", "-k", "uvicorn.workers.UvicornWorker", \
     "--bind", "0.0.0.0:8000", "--workers", "4", "--timeout", "120"]
