"""
Receipt Entity Module

This module defines the Receipt class which represents a financial receipt
with transaction details such as sender, receiver, amount, and description.
"""

from typing import Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class Receipt:
    """
    A class representing a financial receipt with transaction details.
    
    Attributes:
        amount (Optional[str]): The monetary amount of the transaction
        description (Optional[str]): Description or purpose of the transaction
        sender (Optional[str]): Entity that sent/initiated the payment
        receiver (Optional[str]): Entity that received the payment
        value (Optional[str]): Same as amount but with original formatting preserved
    """
    amount: Optional[str] = None
    description: Optional[str] = None
    sender: Optional[str] = None
    receiver: Optional[str] = None
    value: Optional[str] = None

    def __repr__(self) -> str:
        """Return a string representation of the Receipt object."""
        return (f"Receipt(amount={self.amount}, description={self.description}, "
                f"sender={self.sender}, receiver={self.receiver}, value={self.value})")
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert receipt to dictionary for JSON serialization.
        
        Returns:
            Dict[str, Any]: Dictionary representation of the receipt
        """
        return {
            "amount": self.amount,
            "description": self.description,
            "sender": self.sender,
            "receiver": self.receiver,
            "value": self.value
        }
