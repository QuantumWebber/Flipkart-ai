# Stage 1: Build the React Frontend assets (Using full Node image for maximum library compatibility)
FROM node:20 AS build-stage
WORKDIR /frontend
COPY frontend/package.json ./
# Bypass strict peer dependency checks to prevent install crashes
RUN npm install --legacy-peer-deps
COPY frontend/ ./
RUN npm run build

# Stage 2: Set up the Python environment, Headless Chrome, and Server (Full Debian Image)
FROM python:3.11
WORKDIR /app

# Install system dependencies (All compilers and libraries pre-installed in the full image)
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

# Set up a non-root user (Hugging Face Requirement)
RUN useradd -m -u 1000 user

# Set up the working directory inside the user's home directory for write permissions
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH
WORKDIR $HOME/app

# Copy and install python dependencies (using pre-compiled binary wheels)
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Pre-download spaCy models during build phase
RUN python -m spacy download en_core_web_sm

# Copy the remaining project files and set ownership
COPY --chown=user:user . .

# Copy the compiled React assets from Stage 1 into the 'frontend_dist' folder
COPY --from=build-stage /frontend/dist ./frontend_dist
RUN chown -R user:user ./frontend_dist

# Switch to the non-root user for execution
USER user

# Hugging Face Space port
EXPOSE 7860

# Start FastAPI on port 7860
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]