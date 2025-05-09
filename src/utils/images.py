"""
Image Processing Utility Module

This module provides functions for processing receipt images, including
scanning directories for images and extracting text using OCR.
"""

import os
import base64
import io
from typing import List, Dict, Any
from PIL import Image
import pytesseract
import logging


def scan_images_to_text(logger: logging.Logger, 
                        receipts_dir: str = os.getenv("RECEIPTS_DIR")) -> List[Dict[str, Any]]:
    """
    Scan all images in the specified directory and extract text using OCR.
    
    Args:
        logger (logging.Logger): Logger for recording processing information
        receipts_dir (str, optional): Directory containing receipt images.
                                     Defaults to "src/receipts".
    
    Returns:
        List[Dict[str, Any]]: A list of dictionaries containing file info and extracted text.
                             Each dict has keys: 'file', 'text', and 'text_length'.
    """
    results = []
    
    try:
        # Get all files in the receipts directory
        files = [f for f in os.listdir(receipts_dir) 
                if os.path.isfile(os.path.join(receipts_dir, f))]
        
        logger.info(f"Found {len(files)} files in {receipts_dir}")
        
        for file in files:
            file_path = os.path.join(receipts_dir, file)
            
            try:
                # Read and encode the image file
                with open(file_path, "rb") as image_file:
                    base64_string = base64.b64encode(image_file.read()).decode("utf-8")
                
                # Handle data URI format if present
                if "," in base64_string:
                    base64_string = base64_string.split(",")[1]
                
                # Decode base64 and open as image
                image_bytes = base64.b64decode(base64_string)
                image = Image.open(io.BytesIO(image_bytes))
                
                # Extract text using OCR
                text = pytesseract.image_to_string(image)
                
                result = {
                    "file": file,
                    "text": text.strip(),
                    "text_length": len(text)
                }
                results.append(result)
                logger.info(f"Successfully processed {file}, extracted {len(text)} chars")
                
            except Exception as e:
                logger.error(f"Error processing {file}: {str(e)}")
                
        return results
    
    except Exception as e:
        logger.error(f"Error accessing directory {receipts_dir}: {str(e)}")
        return []


def image_to_text(image_data: bytes) -> str:
    """
    Extract text from an image using OCR.
    
    Args:
        image_data (bytes): Raw image data bytes
        
    Returns:
        str: Extracted text from the image
    """
    image = Image.open(io.BytesIO(image_data))
    text = pytesseract.image_to_string(image)
    return text.strip()
