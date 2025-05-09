
"""
Main Application Module

This module serves as the entry point for the receipt processing application,
providing both batch processing functionality and an API server.
"""

import logging
from typing import List, Dict, Any, Optional
import uvicorn

from api import app
from utils.logging import get_logger
from entities.receipt import Receipt


def process_receipts_batch() -> List[Dict[str, Any]]:
    """
    Process receipts in batch mode from the receipts directory.
    
    This function scans the receipts directory for images, extracts text using OCR,
    and processes each receipt with the language model to extract structured information.
    
    Returns:
        List[Dict[str, Any]]: List of processed receipts with extracted information
    """
    from utils.images import scan_images_to_text
    from llm.llm import llm_parse_text_to_receipt
    
    logger = get_logger(__name__)
    logger.info("Starting receipt processing in batch mode")
    
    results = []
    receipts = scan_images_to_text(logger)
    
    for receipt in receipts:
        text = receipt["text"]
        file_name = receipt["file"]
        logger.info(f"Processing receipt: {file_name}")
        
        parsed_receipt = llm_parse_text_to_receipt(logger, text)
        logger.info(f"Parsed receipt: {parsed_receipt}")
        
        results.append({
            "file": file_name,
            "receipt": parsed_receipt.to_dict() if parsed_receipt else None
        })
    
    return results


if __name__ == "__main__":
    # Run the FastAPI application
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)
