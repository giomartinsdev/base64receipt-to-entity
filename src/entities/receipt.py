class Receipt:
    def __init__(self, amount=None, description=None, sender=None, receiver=None, value=None):
        self.amount = amount
        self.description = description
        self.sender = sender
        self.receiver = receiver
        self.value = value

    def __repr__(self):
        return f"Receipt(amount={self.amount}, description={self.description}, sender={self.sender}, receiver={self.receiver}, value={self.value})"
