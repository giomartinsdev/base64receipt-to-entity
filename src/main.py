
from utils.logging import get_logger
from utils.images import scan_images_to_text
from llm.llm import llm_parse_text_to_receipt

if __name__ == "__main__":
    logger = get_logger(__name__)
    logger.info("Starting receipt processing")
    
    receipts = scan_images_to_text(logger)
    for receipt in receipts:
        text = receipt["text"]
        logger.info(f"Processing receipt: {receipt['file']}")
        
        parsed_receipt = llm_parse_text_to_receipt(logger, text)
        logger.info(f"Parsed receipt: {parsed_receipt}")
