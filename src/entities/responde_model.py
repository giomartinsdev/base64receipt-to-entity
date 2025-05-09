
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

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


class ReceiptResponse(BaseModel):
    """
    Model representing structured receipt data extracted from an image.
    
    Attributes:
        amount (Optional[str]): Extracted monetary amount
        description (Optional[str]): Description or purpose of the transaction
        sender (Optional[str]): Entity that sent/initiated the payment
        receiver (Optional[str]): Entity that received the payment
        value (Optional[str]): Same as amount but with original formatting preserved
    """
    description: Optional[str] = Field(None, description="Transaction description")
    sender: Optional[str] = Field(None, description="Sender/initiator of the payment")
    receiver: Optional[str] = Field(None, description="Recipient of the payment")
    value: Optional[str] = Field(None, description="Original formatted monetary value")
