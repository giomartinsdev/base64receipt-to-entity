"""
API Module

This module implements the RESTful API endpoints for receipt processing,
including receipt text extraction, parsing, and data extraction.
"""

import os
from fastapi import FastAPI, HTTPException, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Dict, Any
import uvicorn
import base64
from datetime import datetime
from dotenv import load_dotenv

from src.entities.request_model import Base64Request
from src.entities.responde_model import PingResponse, ReceiptResponse
from src.utils.logging import get_logger
from src.llm.llm import llm_parse_text_to_receipt


load_dotenv(override=True)

app = FastAPI(
    title="Receipt Processing API",
    description="API for processing receipt images and parsing into structured data.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/ping", response_model=PingResponse, tags=["Health"])
def ping() -> PingResponse:
    """
    Health check endpoint to verify API is operational.
    
    Returns:
        PingResponse: Simple response with "pong" message and timestamp
    """
    return PingResponse()


@app.post(
    "/api/base64-to-receipt", 
    response_model=ReceiptResponse,
    tags=["Receipt Processing"],
    status_code=status.HTTP_200_OK
)
async def base64_to_receipt(request: Base64Request) -> Dict[str, Any]:
    """
    Process a receipt image from base64 encoding.
    
    This endpoint decodes a base64-encoded image, extracts text using OCR,
    and then processes the text with a language model to extract structured receipt data.
    
    Args:
        request (Base64Request): Request body containing base64-encoded image
        
    Returns:
        Dict[str, Any]: Structured receipt data
        
    Raises:
        HTTPException: If image processing or text parsing fails
    """
    logger = get_logger(__name__)
    logger.info("Starting receipt processing")
    
    # Extract base64 string
    base64_string = request.text
    if "," in base64_string:
        base64_string = base64_string.split(",")[1]
    
    try:
        # First, decode the base64 image and extract text using OCR
        import io
        from PIL import Image
        import pytesseract
        
        # Decode base64 to image
        image_bytes = base64.b64decode(base64_string)
        image = Image.open(io.BytesIO(image_bytes))
        
        # Extract text using OCR
        extracted_text = pytesseract.image_to_string(image)
        logger.info(f"Extracted text length: {len(extracted_text)}")
        
        # Now process the extracted text with LLM
        parsed_receipt = llm_parse_text_to_receipt(logger, extracted_text)
        if not parsed_receipt:
            logger.error("Failed to parse receipt")
            raise HTTPException(status_code=500, detail="Failed to parse receipt")
        
        logger.info(f"Parsed receipt: {parsed_receipt}")
        return parsed_receipt.to_dict()
    except Exception as e:
        logger.error(f"Error processing receipt: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Global exception handler for unhandled exceptions.
    
    Args:
        request (Request): The request that caused the exception
        exc (Exception): The unhandled exception
        
    Returns:
        JSONResponse: A JSON response with error details
    """
    logger = get_logger(__name__)
    logger.error(f"Unhandled exception: {str(exc)}")
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": str(exc),
            "detail": "An unexpected error occurred",
            "timestamp": datetime.now().isoformat()
        },
    )


if __name__ == "__main__":
    uvicorn.run("api:app", host=os.getenv("API_HOST", "0.0.0.0"), port=os.getenv("API_PORT", 8000), reload=True)
