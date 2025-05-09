# simple_blockchain_py/transaction.py

class Transaction:
    """
    Represents a single transaction in the blockchain.
    """
    def __init__(self, sender: str, recipient: str, amount: float):
        """
        Initializes a new transaction.

        Args:
            sender (str): The address of the sender.
            recipient (str): The address of the recipient.
            amount (float): The amount being transferred.
        """
        self.sender = sender
        self.recipient = recipient
        self.amount = amount

    def to_dict(self) -> dict:
        """
        Returns a dictionary representation of the transaction.
        This is useful for serialization, display, and hashing.
        """
        return self.__dict__

    def __repr__(self) -> str:
        """
        Provides a developer-friendly string representation of the transaction.
        Useful for debugging and logging.
        """
        return f"Transaction(sender='{self.sender}', recipient='{self.recipient}', amount={self.amount})"

if __name__ == '__main__':
    # Example usage (for testing this file directly)
    tx1 = Transaction(sender="Alice", recipient="Bob", amount=50.0)
    print(tx1)
    print(tx1.to_dict())

    tx2 = Transaction(sender="Bob", recipient="Charlie", amount=25.5)
    print(tx2)
    print(tx2.to_dict())