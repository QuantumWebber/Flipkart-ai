# Stage 1: Build the React Frontend assets
FROM node:20-alpine AS build-stage
WORKDIR /frontend
COPY frontend/package.json ./
RUN npm install
COPY frontend/ ./
RUN npm run build

# Stage 2: Set up the Python environment and headless Chrome (MAMAA Standard)
FROM python:3.11

# [1] Install system dependencies as root
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget \
    gnupg \
    unzip \
    curl \
    libgl1-mesa-glx \
    libglib2.0-0 \
    chromium \
    chromium-driver \
    && rm -rf /var/lib/apt/lists/*

# [2] Create a non-root user named "user" with UID 1000 (Hugging Face Requirement)
RUN useradd -m -u 1000 user

# Set up the working directory inside the user's home directory to allow write permissions
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH
WORKDIR $HOME/app

# [3] Copy and install python dependencies (globally as root, then we switch users)
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Pre-download spaCy models globally
RUN python -m spacy download en_core_web_sm

# [4] Copy the remaining backend files and change ownership to the non-root user
COPY --chown=user:user . .

# Copy the compiled React assets from Stage 1 into the container and set permissions
COPY --from=build-stage /frontend/dist ./frontend_dist
RUN chown -R user:user ./frontend_dist

# [5] Switch to the non-root user for execution
USER user

# Hugging Face Spaces exposes port 7860 by default
EXPOSE 7860

# Start FastAPI on port 7860
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]