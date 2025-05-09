
import uvicorn
from api import app
from utils.logging import get_logger

def process_receipts_batch():
    """Legacy function to process receipts in batch mode"""
    from utils.images import scan_images_to_text
    from llm.llm import llm_parse_text_to_receipt
    
    logger = get_logger(__name__)
    logger.info("Starting receipt processing in batch mode")
    
    receipts = scan_images_to_text(logger)
    for receipt in receipts:
        text = receipt["text"]
        logger.info(f"Processing receipt: {receipt['file']}")
        
        parsed_receipt = llm_parse_text_to_receipt(logger, text)
        logger.info(f"Parsed receipt: {parsed_receipt}")

if __name__ == "__main__":
    # Run FastAPI application
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)
