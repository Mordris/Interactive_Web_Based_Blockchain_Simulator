# simple_blockchain_py/transaction.py

class Transaction:
    """
    Represents a single transaction in the blockchain.
    Each transaction has a sender, a recipient, and an amount.
    """
    def __init__(self, sender: str, recipient: str, amount: float):
        """
        Initializes a new transaction.

        Args:
            sender (str): The address or identifier of the sender.
            recipient (str): The address or identifier of the recipient.
            amount (float): The amount being transferred in the transaction.
                            Must be a positive value.
        """
        if not isinstance(sender, str) or not sender:
            raise ValueError("Sender must be a non-empty string.")
        if not isinstance(recipient, str) or not recipient:
            raise ValueError("Recipient must be a non-empty string.")
        if not isinstance(amount, (int, float)) or amount <= 0:
            raise ValueError("Amount must be a positive number.")

        self.sender: str = sender
        self.recipient: str = recipient
        self.amount: float = float(amount) # Ensure amount is float

    def to_dict(self) -> dict:
        """
        Returns a dictionary representation of the transaction.
        This is useful for serialization (e.g., to JSON), display,
        and for creating a consistent structure for hashing within a block.

        Returns:
            dict: A dictionary containing the sender, recipient, and amount.
        """
        return {
            'sender': self.sender,
            'recipient': self.recipient,
            'amount': self.amount
        }

    def __repr__(self) -> str:
        """
        Provides a developer-friendly string representation of the Transaction object.
        Useful for debugging, logging, and direct printing of Transaction instances.

        Returns:
            str: A string representation of the transaction.
        """
        return f"Transaction(sender='{self.sender}', recipient='{self.recipient}', amount={self.amount})"

    def __eq__(self, other) -> bool:
        """
        Compares two Transaction objects for equality based on their attributes.
        Useful for testing and comparisons.
        """
        if not isinstance(other, Transaction):
            return NotImplemented
        return (self.sender == other.sender and
                self.recipient == other.recipient and
                self.amount == other.amount)

# --- Example Usage (for testing this file directly) ---
if __name__ == '__main__':
    print("--- Testing Transaction Class ---")
    try:
        # Valid transaction
        tx1 = Transaction(sender="Alice", recipient="Bob", amount=50.0)
        print(f"Valid Transaction 1: {tx1}")
        print(f"Dictionary representation: {tx1.to_dict()}")

        tx2 = Transaction(sender="Alice", recipient="Bob", amount=50) # Integer amount
        print(f"Valid Transaction 2 (int amount): {tx2}")
        print(f"tx1 == tx2: {tx1 == tx2}") # Should be True

        # Test invalid inputs
        print("\nTesting invalid inputs (expecting ValueErrors):")
        try:
            Transaction(sender="", recipient="Carol", amount=10.0)
        except ValueError as e:
            print(f"Caught expected error for empty sender: {e}")

        try:
            Transaction(sender="Dave", recipient="Eve", amount=-5.0)
        except ValueError as e:
            print(f"Caught expected error for negative amount: {e}")

        try:
            Transaction(sender="Frank", recipient="Grace", amount=0)
        except ValueError as e:
            print(f"Caught expected error for zero amount: {e}")

    except Exception as e:
        print(f"An unexpected error occurred during testing: {e}")