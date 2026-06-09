# Stage 1: Build the React Frontend assets
FROM node:20-alpine AS build-stage
WORKDIR /frontend
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ ./
RUN npm run build

# Stage 2: Set up the Python FastAPI environment, Chrome, and Build Tools
FROM python:3.11-slim
WORKDIR /app

# Install system dependencies, including headless Chromium, Chromium-Driver, Mesa, and C++ Build Tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget \
    gnupg \
    unzip \
    curl \
    libgl1-mesa-glx \
    libglib2.0-0 \
    chromium \
    chromium-driver \
    build-essential \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Install Python requirements
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Pre-download spaCy models during build phase
RUN python -m spacy download en_core_web_sm

# Copy the backend files into the container
COPY . .

# Copy the compiled React assets from Stage 1 into the 'frontend_dist' folder
COPY --from=build-stage /frontend/dist ./frontend_dist

# Hugging Face Spaces exposes port 7860 by default
EXPOSE 7860

# Start FastAPI on port 7860
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]