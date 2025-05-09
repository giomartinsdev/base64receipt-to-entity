from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import uvicorn
import base64

from utils.logging import get_logger
from llm.llm import llm_parse_text_to_receipt
from utils.images import scan_images_to_text
from entities.receipt import Receipt

# Initialize FastAPI app
app = FastAPI(title="Receipt Processing API")

# Define request and response models
class Base64Request(BaseModel):
    text: str

class ReceiptModel(BaseModel):
    amount: Optional[str] = None
    description: Optional[str] = None
    sender: Optional[str] = None
    receiver: Optional[str] = None
    value: Optional[str] = None

class PingResponse(BaseModel):
    message: str = "pong"

class ReceiptScanResult(BaseModel):
    file: str
    receipt: Optional[ReceiptModel] = None
    error: Optional[str] = None

@app.get("/api/ping", response_model=PingResponse)
def ping():
    """Health check endpoint"""
    return PingResponse()

@app.post("/api/base64-to-receipt", response_model=ReceiptModel)
async def base64_to_receipt(request: Base64Request):
    """
    Process a receipt image from base64 encoding
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

@app.get("/api/scan-receipts", response_model=List[ReceiptScanResult])
async def scan_receipts():
    """
    Scan all receipt images in the receipts directory and return extracted data
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
async def general_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"error": str(exc)},
    )

if __name__ == "__main__":
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)
