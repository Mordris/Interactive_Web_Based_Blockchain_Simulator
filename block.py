# simple_blockchain_py/block.py

import hashlib # For SHA-256 hashing
import json    # To serialize data before hashing
import time    # To get timestamps

# We'll import Transaction later when we integrate it. For now, Block focuses on its own structure.
# from transaction import Transaction # Placeholder for future import

class Block:
    """
    Represents a single block in our blockchain.
    """
    def __init__(self, index: int, transactions: list, timestamp: float, previous_hash: str, nonce: int = 0):
        """
        Initializes a new block.

        Args:
            index (int): The position of the block in the chain.
            transactions (list): A list of transactions included in this block.
                                (Initially, this could be a list of dictionaries or strings.
                                Later, it will be a list of Transaction objects).
            timestamp (float): The time the block was created (e.g., using time.time()).
            previous_hash (str): The hash of the preceding block in the chain.
            nonce (int, optional): The nonce used for Proof-of-Work. Defaults to 0.
        """
        self.index: int = index
        self.transactions: list = transactions # For now, let's assume these are simple dicts or will be
        self.timestamp: float = timestamp
        self.previous_hash: str = previous_hash
        self.nonce: int = nonce
        self.hash: str = self.calculate_hash() # Calculate hash upon initialization

    def calculate_hash(self) -> str:
        """
        Calculates the SHA-256 hash of the block's content.
        The content includes index, transactions, timestamp, previous_hash, and nonce.
        Transactions need to be handled carefully to ensure consistent hashing.
        """
        # Create a dictionary of the block's content
        block_content = {
            'index': self.index,
            'transactions': self.transactions, # How transactions are serialized is important
            'timestamp': self.timestamp,
            'previous_hash': self.previous_hash,
            'nonce': self.nonce
        }

        # Serialize the dictionary to a JSON string.
        # sort_keys=True ensures that the dictionary keys are always in the same order,
        # producing a consistent string for hashing.
        # Using .encode('utf-8') converts the string to bytes, which hashlib expects.
        block_string = json.dumps(block_content, sort_keys=True).encode('utf-8')

        # Create a SHA-256 hash object
        sha256_hash = hashlib.sha256()

        # Update the hash object with the block string (bytes)
        sha256_hash.update(block_string)

        # Return the hexadecimal representation of the hash
        return sha256_hash.hexdigest()

    def __repr__(self) -> str:
        """
        Provides a developer-friendly string representation of the block.
        """
        return (f"Block(index={self.index}, "
                f"transactions_count={len(self.transactions)}, "
                f"timestamp={self.timestamp}, "
                f"previous_hash='{self.previous_hash}', "
                f"nonce={self.nonce}, "
                f"hash='{self.hash}')")


if __name__ == '__main__':
    # Example usage (for testing this file directly)
    # For now, transactions are just simple dictionaries for testing the Block class itself
    sample_transactions_for_block_test = [
        {'sender': 'Alice', 'recipient': 'Bob', 'amount': 50},
        {'sender': 'Bob', 'recipient': 'Charlie', 'amount': 25}
    ]

    block1 = Block(
        index=0,
        transactions=sample_transactions_for_block_test,
        timestamp=time.time(),
        previous_hash="0" # Genesis block typically has "0" or a similar placeholder
    )
    print(block1)
    print(f"Block 1 Hash: {block1.hash}")

    # Test if changing nonce changes the hash
    block1_copy = Block(0, sample_transactions_for_block_test, block1.timestamp, "0", nonce=0)
    block1_copy_different_nonce = Block(0, sample_transactions_for_block_test, block1.timestamp, "0", nonce=1)
    print(f"Hash with nonce 0: {block1_copy.hash}")
    print(f"Hash with nonce 1: {block1_copy_different_nonce.hash}")
    assert block1_copy.hash != block1_copy_different_nonce.hash, "Changing nonce should change hash!"

    # Test if changing transactions changes the hash
    different_transactions = [{'sender': 'Dave', 'recipient': 'Eve', 'amount': 10}]
    block1_copy_different_tx = Block(0, different_transactions, block1.timestamp, "0", nonce=0)
    print(f"Hash with different transactions: {block1_copy_different_tx.hash}")
    assert block1_copy.hash != block1_copy_different_tx.hash, "Changing transactions should change hash!"