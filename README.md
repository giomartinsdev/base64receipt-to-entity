# Receipt Image Processing and Data Extraction

A system for extracting structured data from receipt images using OCR and Language Models.

## Overview

This project provides a system to process images of receipts, extract text using OCR (Optical Character Recognition), and then leverage Language Models to parse the text into structured data. The system is designed to identify key information such as amount, sender, receiver, and description from receipts.

## Features

- **Image Processing**: Process receipt images from files or base64-encoded data
- **OCR Integration**: Extract text from images using Tesseract OCR
- **Language Model Processing**: Parse receipt text to extract structured data
- **RESTful API**: Process receipts via HTTP endpoints
- **Memory Efficient**: Handles large images with built-in memory optimization
- **GPU/CPU Flexibility**: Automatically adapts between GPU and CPU processing

## Architecture

The system is organized into several modules:

- `entities`: Data models representing receipts
- `llm`: Language model integration for text processing
- `utils`: Utility functions for image processing, text handling, and logging
- `api`: REST API for accessing functionality through HTTP endpoints

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/ping` | GET | Health check endpoint |
| `/api/base64-to-receipt` | POST | Process a base64-encoded receipt image |
| `/api/scan-receipts` | GET | Scan and process all receipts in the receipts directory |

## Getting Started

### Prerequisites

- Python 3.8+
- CUDA-compatible GPU (optional, for accelerated processing)
- Tesseract OCR

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd map-receipt-image-to-entity
```

2. Create and activate a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Install Tesseract OCR:
```bash
# Ubuntu/Debian
sudo apt-get install tesseract-ocr

# macOS
brew install tesseract

# Windows
# Download installer from: https://github.com/UB-Mannheim/tesseract/wiki
```

### Running the Server

Start the API server:
```bash
uvicorn src.api:app --host 0.0.0.0 --port 8000  ## you can change host and port  
```

The API will be available at `http://localhost:8000`.

### Docker Deployment

Build and run using Docker:

```bash
docker-compose up -d
```

## Usage Examples

### Process a Base64 Image

```bash
curl -X POST http://localhost:8000/api/base64-to-receipt \
  -H "Content-Type: application/json" \
  -d '{"text": "base64-encoded-image-data"}'
```

### Check Health

```bash
curl http://localhost:8000/api/ping
```

## Memory Optimization

The system includes several memory optimization features:

1. **Smart Text Truncation**: Automatically truncates long texts while preserving important content
2. **Device Management**: Automatically selects GPU or CPU based on availability
3. **Memory-Efficient Settings**: Uses optimized settings for language model inference
4. **CPU Fallback**: Automatically falls back to CPU processing when GPU memory is exhausted

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
