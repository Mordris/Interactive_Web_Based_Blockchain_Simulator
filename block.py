# simple_blockchain_py/block.py

import hashlib # For SHA-256 hashing
import json    # To serialize data (like transactions) before hashing
import time    # To get timestamps for block creation

# Note: The Transaction class itself is not directly used by Block,
# as blocks store transactions as dictionaries for consistent hashing.
# However, a type hint might still be useful for clarity if transactions
# were passed as Transaction objects initially.

class Block:
    """
    Represents a single block in our blockchain.
    A block contains an index, a list of transactions (stored as dictionaries),
    a timestamp, the hash of the preceding block, a nonce (for Proof-of-Work),
    and its own calculated hash.
    """
    def __init__(self, index: int, transactions: list[dict], timestamp: float, previous_hash: str, nonce: int = 0):
        """
        Initializes a new block.

        Args:
            index (int): The position of the block in the chain (e.g., 0 for genesis).
            transactions (list[dict]): A list of transactions included in this block.
                                       Each transaction should be a dictionary.
            timestamp (float): The time the block was created (Unix timestamp, e.g., using time.time()).
            previous_hash (str): The hash of the preceding block in the chain. For the genesis
                                 block, this is typically "0" or a similar placeholder.
            nonce (int, optional): The nonce value found during Proof-of-Work. Defaults to 0.
                                   This will be adjusted during mining.
        """
        self.index: int = index
        self.transactions: list[dict] = transactions # Store transactions as list of dicts
        self.timestamp: float = timestamp
        self.previous_hash: str = previous_hash
        self.nonce: int = nonce
        # The hash of the block is calculated based on its content, including the nonce.
        # It's calculated upon initialization and will be recalculated during mining.
        self.hash: str = self.calculate_hash()

    def calculate_hash(self) -> str:
        """
        Calculates the SHA-256 hash of the block's content.
        The content includes the block's index, its transactions (as a sorted JSON string),
        timestamp, previous_hash, and the current nonce.

        Ensuring transactions are consistently serialized (e.g., sorted keys in JSON)
        is crucial for deterministic hashing.

        Returns:
            str: The hexadecimal string representation of the SHA-256 hash.
        """
        # Create a dictionary of the block's content to be hashed.
        # Using a dictionary ensures that we consistently include all necessary fields.
        block_content = {
            'index': self.index,
            # Serialize transactions to a JSON string with sorted keys to ensure
            # that the order of items within each transaction dictionary and the order
            # of transactions themselves (if not already sorted) doesn't affect the hash.
            # For simplicity here, we assume the list of transactions is already in a fixed order
            # as prepared by the Blockchain class before being passed to the Block.
            'transactions': self.transactions, # These should be dicts
            'timestamp': self.timestamp,
            'previous_hash': self.previous_hash,
            'nonce': self.nonce
        }

        # Serialize the entire block content dictionary to a JSON string.
        # `sort_keys=True` is critical: it ensures that dictionary keys are always
        # in the same alphabetical order, producing a consistent string for hashing,
        # regardless of Python's internal dictionary ordering.
        # `.encode('utf-8')` converts the string to bytes, which hashlib expects.
        block_string = json.dumps(block_content, sort_keys=True).encode('utf-8')

        # Create a SHA-256 hash object.
        sha256_hasher = hashlib.sha256()

        # Update the hash object with the block's byte string.
        sha256_hasher.update(block_string)

        # Return the hexadecimal representation of the computed hash.
        return sha256_hasher.hexdigest()

    def __repr__(self) -> str:
        """
        Provides a developer-friendly string representation of the Block object.
        Useful for debugging, logging, and direct printing of Block instances.

        Returns:
            str: A string representation of the block.
        """
        # Truncate hash for display if it's too long
        short_hash = self.hash[:10] + "..." if len(self.hash) > 10 else self.hash
        short_prev_hash = self.previous_hash[:10] + "..." if len(self.previous_hash) > 10 else self.previous_hash
        return (f"Block(index={self.index}, "
                f"tx_count={len(self.transactions)}, "
                # f"timestamp={self.timestamp:.2f}, " # Formatted timestamp
                f"prev_hash='{short_prev_hash}', "
                f"nonce={self.nonce}, "
                f"hash='{short_hash}')")

# --- Example Usage (for testing this file directly) ---
if __name__ == '__main__':
    print("--- Testing Block Class ---")
    # Sample transactions (as dictionaries, which is how they are stored in the Block)
    sample_transactions_for_block = [
        {'sender': 'Alice', 'recipient': 'Bob', 'amount': 50.0},
        {'sender': 'Bob', 'recipient': 'Charlie', 'amount': 25.5}
    ]

    # Create a genesis block example
    genesis_block = Block(
        index=0,
        transactions=[], # Genesis block usually has no user transactions
        timestamp=time.time(),
        previous_hash="0" # Conventional previous hash for the genesis block
    )
    print(f"Genesis Block: {genesis_block}")
    print(f"Genesis Block Full Hash: {genesis_block.hash}")

    # Create a subsequent block example
    block_one = Block(
        index=1,
        transactions=sample_transactions_for_block,
        timestamp=time.time(),
        previous_hash=genesis_block.hash, # Linked to the genesis block
        nonce=123 # Example nonce
    )
    print(f"Block One: {block_one}")
    print(f"Block One Full Hash: {block_one.hash}")

    # Test if changing nonce changes the hash
    block_one_alt_nonce = Block(
        index=1,
        transactions=sample_transactions_for_block,
        timestamp=block_one.timestamp, # Keep timestamp same for direct comparison
        previous_hash=genesis_block.hash,
        nonce=124 # Different nonce
    )
    print(f"Block One (Alt Nonce): {block_one_alt_nonce}")
    print(f"Block One (Alt Nonce) Full Hash: {block_one_alt_nonce.hash}")
    assert block_one.hash != block_one_alt_nonce.hash, "Changing nonce should result in a different hash."
    print("Nonce change test PASSED.")

    # Test if changing transactions changes the hash
    different_transactions = [{'sender': 'Dave', 'recipient': 'Eve', 'amount': 10.0}]
    block_one_alt_tx = Block(
        index=1,
        transactions=different_transactions,
        timestamp=block_one.timestamp,
        previous_hash=genesis_block.hash,
        nonce=123 # Same nonce as original block_one
    )
    print(f"Block One (Alt Transactions): {block_one_alt_tx}")
    print(f"Block One (Alt Transactions) Full Hash: {block_one_alt_tx.hash}")
    assert block_one.hash != block_one_alt_tx.hash, "Changing transactions should result in a different hash."
    print("Transaction change test PASSED.")