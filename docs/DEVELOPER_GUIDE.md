# Developer Guide

This guide provides detailed information for developers working on the Receipt Image Processing project.

## Project Structure

```
/
├── config/                # Configuration files
│   └── settings.toml      # Application settings
├── requirements.txt       # Python dependencies
├── src/                   # Source code
│   ├── __init__.py        # Package initialization
│   ├── api.py             # FastAPI implementation
│   ├── main.py            # Application entry point
│   ├── entities/          # Data models
│   │   └── receipt.py     # Receipt entity
│   ├── llm/               # Language model integration
│   │   ├── llm.py         # LLM processing logic
│   │   └── prompt.py      # Prompts for LLM
│   └── utils/             # Utility modules
│       ├── images.py      # Image processing utilities
│       ├── logging.py     # Logging configuration
│       └── text.py        # Text processing utilities
├── Dockerfile             # Docker configuration
└── docker-compose.yml     # Docker Compose configuration
```

## Key Components

### Receipt Entity

The `Receipt` class (in `entities/receipt.py`) represents the structured data extracted from receipts:

```python
@dataclass
class Receipt:
    amount: Optional[str] = None         # Monetary amount
    description: Optional[str] = None    # Transaction description
    sender: Optional[str] = None         # Payment sender
    receiver: Optional[str] = None       # Payment receiver
    value: Optional[str] = None          # Original formatted monetary value
```

### Language Model Processing

The LLM processing is handled by modules in the `llm/` directory:

1. `llm.py`: Contains functions for processing text with language models
2. `prompt.py`: Contains prompt templates for guiding the language model

The key function is `llm_parse_text_to_receipt`, which:
- Handles text truncation for long inputs
- Processes text with a language model
- Extracts structured data from the model output
- Returns a Receipt object

### Image Processing

The `utils/images.py` module provides functions for working with receipt images:

- `scan_images_to_text`: Scans a directory for receipt images and extracts text
- `image_to_text`: Extracts text from a single image

### API Endpoints

The FastAPI implementation in `api.py` exposes the following endpoints:

1. `GET /api/ping`: Simple health check
2. `POST /api/base64-to-receipt`: Process a base64-encoded receipt image
3. `GET /api/scan-receipts`: Scan and process all receipts in the receipts directory

## Memory Management

The project uses several strategies to optimize memory usage:

1. **Smart Text Truncation**: 
   ```python
   # Keep beginning (70%) and end (30%) of the text
   beginning = text[:int(max_length * 0.7)]
   end = text[-(int(max_length * 0.3)):]
   text = beginning + end
   ```

2. **GPU Memory Management**:
   ```python
   # When using device_map="auto", don't specify device parameter
   pipeline(
       "text-generation", 
       model="google/gemma-3-1b-it",
       torch_dtype=torch.bfloat16,
       model_kwargs={
           "low_cpu_mem_usage": True,
           "device_map": "auto"
       }
   )
   ```

3. **CPU Fallback**: Automatically switches to CPU processing when GPU memory is insufficient

## Error Handling

The application uses a comprehensive error handling approach:

1. **Function-Level Error Handling**: Each function includes try/except blocks for specific error cases
2. **Global Exception Handler**: The API includes a global exception handler for unhandled exceptions
3. **Structured Logging**: Detailed logging throughout the application for debugging

## Extending the Project

### Adding New Models

To add support for a new language model:

1. Update the `get_pipeline` function in `llm/llm.py` with the new model information
2. Adjust the prompt in `llm/prompt.py` if needed for the new model
3. Test with sample receipts to ensure accurate extraction

### Adding New Receipt Fields

To extract additional fields from receipts:

1. Update the `Receipt` class in `entities/receipt.py` with new fields
2. Modify the prompt in `llm/prompt.py` to instruct the model to extract these fields
3. Update the `llm_parse_text_to_receipt` function to handle the new fields

## Testing

To run tests:

```bash
pytest tests/
```

## Common Issues and Solutions

### GPU Out of Memory

If you encounter GPU memory issues:

1. Reduce `max_length` in `llm_parse_text_to_receipt` function
2. Adjust Docker memory limits in `docker-compose.yml`
3. Set environment variable: `PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True`

### OCR Quality Issues

If OCR text extraction is poor:

1. Check Tesseract installation and version
2. Pre-process images (resize, increase contrast, etc.)
3. Consider using a different OCR engine


## Issues with ContainerConfig
# Stop and remove all containers
1. `docker stop $(docker ps -a -q) 2>/dev/null || true`
2. `docker rm $(docker ps -a -q) 2>/dev/null || true`