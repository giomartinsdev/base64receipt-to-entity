FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONPATH=/app \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=on

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libffi-dev \
    tesseract-ocr \
    libtesseract-dev \
    libpng-dev \
    libjpeg-dev \
    libtiff-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirements.txt .

# Install dependencies
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Copy the project code
COPY . .

# Create directories
RUN mkdir -p src/receipts

# Expose the port
EXPOSE 8000

# Run the app
CMD ["uvicorn", "src.api:app", "--host", "0.0.0.0", "--port", "8000"]