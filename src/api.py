"""
API Module

This module implements the RESTful API endpoints for receipt processing,
including receipt text extraction, parsing, and data extraction.
"""

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
import uvicorn
import base64
import io
from datetime import datetime

from utils.logging import get_logger
from llm.llm import llm_parse_text_to_receipt
from utils.images import scan_images_to_text, image_to_text
from entities.receipt import Receipt

# Initialize FastAPI app
app = FastAPI(
    title="Receipt Processing API",
    description="API for processing receipt images and extracting structured information",
    version="1.0.0"
)

# Define request and response models
class Base64Request(BaseModel):
    """
    Request model for submitting a base64-encoded receipt image.
    
    Attributes:
        text (str): Base64-encoded image data, with or without the data URI prefix
    """
    text: str = Field(..., description="Base64-encoded image data")


class ReceiptModel(BaseModel):
    """
    Model representing structured receipt data extracted from an image.
    
    Attributes:
        amount (Optional[str]): Extracted monetary amount
        description (Optional[str]): Description or purpose of the transaction
        sender (Optional[str]): Entity that sent/initiated the payment
        receiver (Optional[str]): Entity that received the payment
        value (Optional[str]): Same as amount but with original formatting preserved
    """
    amount: Optional[str] = Field(None, description="Monetary amount")
    description: Optional[str] = Field(None, description="Transaction description")
    sender: Optional[str] = Field(None, description="Sender/initiator of the payment")
    receiver: Optional[str] = Field(None, description="Recipient of the payment")
    value: Optional[str] = Field(None, description="Original formatted monetary value")


class PingResponse(BaseModel):
    """
    Simple response model for API health check.
    
    Attributes:
        message (str): Status message, defaults to "pong"
        timestamp (str): Current timestamp when the request was processed
    """
    message: str = Field("pong", description="Health check response")
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat(), 
                          description="Response timestamp")


class ReceiptScanResult(BaseModel):
    """
    Result of scanning and processing a receipt image.
    
    Attributes:
        file (str): Name of the processed file
        receipt (Optional[ReceiptModel]): Structured receipt data if processing succeeded
        error (Optional[str]): Error message if processing failed
    """
    file: str = Field(..., description="Filename of the processed receipt")
    receipt: Optional[ReceiptModel] = Field(None, description="Extracted receipt data")
    error: Optional[str] = Field(None, description="Error message if processing failed")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with actual origins
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
    response_model=ReceiptModel,
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

@app.get(
    "/api/scan-receipts", 
    response_model=List[ReceiptScanResult],
    tags=["Receipt Processing"],
    status_code=status.HTTP_200_OK
)
async def scan_receipts() -> List[Dict[str, Any]]:
    """
    Scan all receipt images in the receipts directory and extract structured data.
    
    This endpoint processes all image files in the configured receipts directory,
    extracts text using OCR, and parses the text to extract structured receipt information.
    
    Returns:
        List[Dict[str, Any]]: List of processed receipts with extracted data
        
    Raises:
        HTTPException: If directory scanning or processing fails
    """
    logger = get_logger(__name__)
    logger.info("Starting batch receipt scanning")
    
    try:
        # Scan images and extract text
        receipt_texts = scan_images_to_text(logger)
        
        # Process each receipt with LLM
        results = []
        for receipt_item in receipt_texts:
            try:
                text = receipt_item["text"]
                file_name = receipt_item["file"]
                
                logger.info(f"Processing receipt: {file_name}")
                parsed_receipt = llm_parse_text_to_receipt(logger, text)
                
                if parsed_receipt:
                    result = {
                        "file": file_name,
                        "receipt": parsed_receipt.to_dict()
                    }
                    results.append(result)
                else:
                    results.append({
                        "file": file_name,
                        "error": "Failed to parse receipt"
                    })
            except Exception as e:
                logger.error(f"Error processing receipt {receipt_item['file']}: {str(e)}")
                results.append({
                    "file": receipt_item["file"],
                    "error": str(e)
                })
        
        return results
    except Exception as e:
        logger.error(f"Error scanning receipts: {str(e)}")
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
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)
