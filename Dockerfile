# Set default Python version
ARG PYTHON_VERSION=3.11

FROM --platform=$BUILDPLATFORM python:3.12-slim AS python3.12
FROM --platform=$BUILDPLATFORM python:3.11-slim AS python3.11
FROM --platform=$BUILDPLATFORM python:3.10-slim AS python3.10
FROM --platform=$BUILDPLATFORM python:3.9-slim AS python3.9
FROM --platform=$BUILDPLATFORM python:3.8-slim AS python3.8

FROM python${PYTHON_VERSION} AS final

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install and configure Jupyter
RUN python -m pip install ipykernel && \
    python -m ipykernel install --user && \
    jupyter kernelspec list

# Copy entrypoint scripts
COPY entrypoint.py .
COPY entrypoint.sh .
RUN chmod +x entrypoint.sh

# Set the entrypoint
ENTRYPOINT ["/app/entrypoint.sh"] 