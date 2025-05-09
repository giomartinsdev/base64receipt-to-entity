import os
import base64
import io
from PIL import Image
import pytesseract

def scan_images_to_text(logger):
    receipts_dir = "src/receipts"
    results = []
    
    try:
        files = [f for f in os.listdir(receipts_dir) if os.path.isfile(os.path.join(receipts_dir, f))]
        
        for file in files:
            file_path = os.path.join(receipts_dir, file)
            
            try:
                with open(file_path, "rb") as image_file:
                    base64_string = base64.b64encode(image_file.read()).decode("utf-8")
                
                if "," in base64_string:
                    base64_string = base64_string.split(",")[1]
                    
                image_bytes = base64.b64decode(base64_string)
                image = Image.open(io.BytesIO(image_bytes))
                text = pytesseract.image_to_string(image)
                
                result = {
                    "file": file,
                    "text": text.strip(),
                    "text_length": len(text)
                }
                results.append(result)
                
            except Exception as e:
                logger.error(f"Error processing {file}: {str(e)}")
                
        return results
    
    except Exception as e:
        logger.error(f"Error accessing directory: {str(e)}")
        return []
