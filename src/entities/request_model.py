from pydantic import BaseModel, Field

class Base64Request(BaseModel):
    """
    Request model for submitting a base64-encoded receipt image.
    
    Attributes:
        text (str): Base64-encoded image data, with or without the data URI prefix
    """
    text: str = Field(..., description="Base64-encoded image data")




