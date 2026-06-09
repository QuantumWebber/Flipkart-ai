# Use the robust full Debian Python image
FROM python:3.11

# Install system dependencies
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

# Set up the non-root user (Hugging Face Requirement)
RUN useradd -m -u 1000 user

# Set up the working directory inside the user's home directory
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH
WORKDIR $HOME/app

# Copy and install python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Pre-download spaCy models globally
RUN python -m spacy download en_core_web_sm

# Copy the remaining project files (including your pre-built frontend_dist)
COPY --chown=user:user . .

# Switch to the non-root user for execution
USER user

# Hugging Face Space port
EXPOSE 7860

# Start FastAPI
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]