FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies (including tesseract for OCR)
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Create necessary directories
RUN mkdir -p /app/src/receipts

# Expose the port
EXPOSE 8000

# Set the entry point
CMD ["python", "src/main.py"]
