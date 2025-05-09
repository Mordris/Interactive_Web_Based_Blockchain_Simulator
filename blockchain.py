# simple_blockchain_py/blockchain.py

import time
import json
from block import Block         # Represents individual blocks in the chain
from transaction import Transaction # Represents individual transactions

class Blockchain:
    """
    Manages a chain of blocks, handles pending transactions,
    implements Proof-of-Work for mining, and provides functionality
    to save and load the blockchain state.
    """
    def __init__(self, difficulty: int = 2, mining_reward: float = 100.0):
        """
        Initializes the blockchain.

        Args:
            difficulty (int): The number of leading zeros required for a valid PoW hash.
                              A higher difficulty increases the computational effort for mining.
            mining_reward (float): The amount awarded to a miner for successfully mining a block.
        """
        self.chain: list[Block] = []  # Stores the actual sequence of blocks
        self.pending_transactions: list[Transaction] = [] # Transactions awaiting inclusion in a block
        self.difficulty: int = int(difficulty) # Ensure difficulty is an integer
        self.mining_reward: float = float(mining_reward) # Ensure reward is a float

        # The genesis block is the first block in any blockchain.
        # It's created when the blockchain is first initialized if no chain is loaded.
        # self.create_genesis_block() # This will be called if loading fails or for a new chain

    def create_genesis_block(self):
        """
        Creates the first block in the chain (the "genesis block").
        This block typically has index 0, no user transactions, and a conventional
        previous_hash (e.g., "0"). It does not require Proof-of-Work in this simulation
        to simplify initialization, or its PoW is trivial.
        """
        print("Creating Genesis Block...")
        # For the genesis block, transactions list is empty, and previous_hash is "0".
        # Nonce can be 0 as PoW is often skipped or simplified for genesis.
        genesis_block = Block(
            index=0,
            transactions=[],
            timestamp=time.time(),
            previous_hash="0",
            nonce=0 # Genesis block often has a fixed nonce or skips intensive PoW
        )
        # The hash for the genesis block is calculated by its __init__ method.
        # If a specific PoW were required for genesis, it would be applied here.
        self.chain.append(genesis_block)
        print(f"Genesis Block created: {genesis_block}")

    def get_latest_block(self) -> Block | None:
        """
        Returns the most recently added block in the chain.

        Returns:
            Block | None: The last block in the chain, or None if the chain is empty.
        """
        if not self.chain:
            return None
        return self.chain[-1]

    def add_transaction(self, sender: str, recipient: str, amount: float) -> int:
        """
        Creates a new transaction and adds it to the list of pending transactions.
        These transactions will be included in the next block that is mined.

        Args:
            sender (str): The address/identifier of the transaction sender.
            recipient (str): The address/identifier of the transaction recipient.
            amount (float): The amount to be transferred.

        Returns:
            int: The index of the block to which this transaction will likely be added
                 (i.e., current latest block index + 1). Returns -1 on failure.
        """
        try:
            transaction = Transaction(sender=sender, recipient=recipient, amount=amount)
            self.pending_transactions.append(transaction)
            print(f"Transaction added to pending pool: {transaction}")
            latest_block = self.get_latest_block()
            if latest_block:
                return latest_block.index + 1
            return 0 # If chain is empty (before genesis is confirmed by load/create logic)
        except ValueError as e:
            print(f"Error adding transaction: {e}")
            return -1 # Indicate failure

    def proof_of_work(self, block: Block) -> str:
        """
        Implements a simple Proof-of-Work (PoW) algorithm.
        The goal is to find a 'nonce' value for the given block such that
        the block's hash starts with a specific number of leading zeros,
        as defined by `self.difficulty`.

        Args:
            block (Block): The block for which to find a valid nonce and hash.

        Returns:
            str: The valid hash found for the block after PoW.
        """
        print(f"Mining block #{block.index} with difficulty {self.difficulty} (target: {'0'*self.difficulty}...).")
        block.nonce = 0  # Start nonce from 0 for each mining attempt
        computed_hash = block.calculate_hash()
        target_prefix = '0' * self.difficulty

        # Keep incrementing the nonce and recalculating the hash until it meets the difficulty target.
        while not computed_hash.startswith(target_prefix):
            block.nonce += 1
            computed_hash = block.calculate_hash()
            # Optional: Print progress for very high difficulties or long mining times
            # if block.nonce % 100000 == 0 and block.nonce > 0:
            #     print(f"  ...mining (nonce: {block.nonce}, hash: {computed_hash[:10]}...)")

        print(f"Block successfully mined! Nonce: {block.nonce}, Hash: {computed_hash}")
        block.hash = computed_hash  # CRITICAL: Update the block's hash with the valid one found by PoW.
        return computed_hash

    def mine_pending_transactions(self, mining_reward_address: str) -> Block | None:
        """
        Mines a new block containing all transactions currently in the pending pool.
        This involves:
        1. Creating a "reward" transaction for the miner.
        2. Bundling this reward with pending user transactions.
        3. Creating a new block with these transactions.
        4. Performing Proof-of-Work on the new block to find a valid hash.
        5. Adding the successfully mined block to the chain.
        6. Clearing the list of pending transactions.

        Args:
            mining_reward_address (str): The address to which the mining reward will be sent.

        Returns:
            Block | None: The newly mined block if successful, or None if there were
                          no transactions to mine (and difficulty > 0) or an error occurred.
        """
        if not self.pending_transactions and self.difficulty > 0:
            # Don't mine empty blocks if there's actual difficulty, unless specifically intended.
            print("No pending transactions to mine.")
            return None

        print(f"\nAttempting to mine new block for {len(self.pending_transactions)} pending transactions...")

        # Create the mining reward transaction. In a real system, this creates new currency.
        # Here, it's a conceptual transaction.
        reward_tx = Transaction(
            sender="network",  # A system identifier for the reward source
            recipient=mining_reward_address,
            amount=self.mining_reward
        )
        # Add the reward transaction to the list of transactions for this new block.
        # It's common for the reward (coinbase) transaction to be the first in the block.
        transactions_for_new_block_objects = [reward_tx] + self.pending_transactions

        latest_block = self.get_latest_block()
        if not latest_block:
            print("Error: Cannot mine without a genesis block or existing chain.")
            return None

        new_block = Block(
            index=latest_block.index + 1,
            # Transactions are stored as dictionaries in the Block for consistent hashing.
            transactions=[tx.to_dict() for tx in transactions_for_new_block_objects],
            timestamp=time.time(),
            previous_hash=latest_block.hash
            # Nonce will be determined by proof_of_work. Hash will be set by PoW.
        )

        # Perform Proof-of-Work to find the valid nonce and hash for the new block.
        self.proof_of_work(new_block) # This method updates new_block.hash internally.

        # Add the newly mined block to the blockchain.
        self.chain.append(new_block)
        print(f"Block #{new_block.index} successfully mined and added to the chain.")

        # Clear the pending transactions pool as they are now included in a block.
        self.pending_transactions = []

        return new_block

    def is_chain_valid(self) -> bool:
        """
        Validates the integrity of the entire blockchain.
        It checks several conditions for each block (except genesis for some rules):
        1. Data Integrity: Verifies that each block's stored hash matches a recalculation
           of its content (using its stored nonce).
        2. Link Integrity: Ensures that each block's `previous_hash` correctly points to
           the actual hash of the preceding block in the chain.
        3. Proof-of-Work Validity: Confirms that each block's hash satisfies the
           blockchain's current difficulty requirement (starts with '0' * difficulty).

        Returns:
            bool: True if the entire blockchain is valid, False otherwise.
        """
        print("\nValidating blockchain integrity...")
        if not self.chain:
            print("Blockchain is empty, nothing to validate.")
            return True # An empty chain (before genesis) can be considered valid in some contexts

        # 1. Validate the Genesis Block separately (hash integrity, PoW if applicable)
        genesis_block = self.chain[0]
        if genesis_block.index != 0 or genesis_block.previous_hash != "0":
            print("Genesis block malformed (index or previous_hash).")
            return False
        
        # Re-calculate genesis block hash to check for tampering
        # Create a temporary block instance to avoid modifying the one in the chain during check
        temp_genesis = Block(genesis_block.index, genesis_block.transactions,
                             genesis_block.timestamp, genesis_block.previous_hash, genesis_block.nonce)
        if genesis_block.hash != temp_genesis.calculate_hash():
            print(f"Genesis Block data integrity compromised!")
            print(f"  Stored hash: {genesis_block.hash}")
            print(f"  Recalculated hash: {temp_genesis.calculate_hash()}")
            return False
        
        # Optional: Check PoW for genesis if it's supposed to have one.
        # Here, we assume genesis might not strictly follow self.difficulty if self.difficulty > 0.
        # If self.difficulty is 0, any hash is fine.
        # If strict PoW for genesis is needed, this check should be unconditional or configurable.

        # 2. Validate the rest of the chain
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i-1]

            # a. Check current block's hash integrity
            # Create a temporary block with current_block's data to recalculate its hash
            temp_current_block = Block(current_block.index, current_block.transactions,
                                       current_block.timestamp, current_block.previous_hash,
                                       current_block.nonce)
            if current_block.hash != temp_current_block.calculate_hash():
                print(f"Data integrity compromised at Block #{current_block.index}.")
                print(f"  Stored hash:      {current_block.hash}")
                print(f"  Recalculated hash: {temp_current_block.calculate_hash()}")
                return False

            # b. Check the chain link (previous_hash)
            if current_block.previous_hash != previous_block.hash:
                print(f"Chain broken: Previous hash mismatch at Block #{current_block.index}.")
                print(f"  Block {current_block.index} previous_hash: {current_block.previous_hash}")
                print(f"  Block {previous_block.index} actual hash:    {previous_block.hash}")
                return False

            # c. Check Proof-of-Work for the current block
            target_prefix = '0' * self.difficulty
            if self.difficulty > 0 and not current_block.hash.startswith(target_prefix):
                # This check is critical. If difficulty is 0, any hash is "valid" by PoW.
                print(f"Proof of Work invalid for Block #{current_block.index}.")
                print(f"  Hash: {current_block.hash} (Difficulty: {self.difficulty}, Target Prefix: '{target_prefix}')")
                return False

        print("Blockchain is valid.")
        return True

    def to_json_serializable(self) -> dict:
        """
        Converts the entire blockchain state (chain, pending transactions, settings)
        into a dictionary format that is directly serializable to JSON.

        Returns:
            dict: A dictionary representing the blockchain state.
        """
        return {
            "chain": [block.__dict__ for block in self.chain], # Block objects to dicts
            "pending_transactions": [tx.to_dict() for tx in self.pending_transactions], # Transaction objects to dicts
            "difficulty": self.difficulty,
            "mining_reward": self.mining_reward
        }

    @classmethod
    def from_json_serializable(cls, data: dict) -> 'Blockchain':
        """
        Creates a Blockchain instance by loading its state from a
        JSON-serializable dictionary (typically obtained from a JSON file).

        Args:
            data (dict): The dictionary containing the blockchain state.

        Returns:
            Blockchain: A new Blockchain instance populated with the loaded data.
        """
        # Initialize with loaded or default difficulty and mining reward
        loaded_difficulty = data.get('difficulty', 2) # Default to 2 if not found
        loaded_mining_reward = data.get('mining_reward', 100.0) # Default reward
        
        blockchain_instance = cls(difficulty=loaded_difficulty, mining_reward=loaded_mining_reward)
        
        # Reconstruct pending transactions from their dictionary representations
        blockchain_instance.pending_transactions = [
            Transaction(sender=tx_data['sender'], recipient=tx_data['recipient'], amount=tx_data['amount'])
            for tx_data in data.get('pending_transactions', [])
        ]

        # Reconstruct the chain of blocks
        blockchain_instance.chain = [] # Start with an empty chain before populating
        for block_data in data.get('chain', []):
            # Create a Block instance from the dictionary data.
            # block_data['transactions'] should already be a list of transaction dictionaries.
            block = Block(
                index=block_data['index'],
                transactions=block_data['transactions'],
                timestamp=block_data['timestamp'],
                previous_hash=block_data['previous_hash'],
                nonce=block_data['nonce']
            )
            # The hash is calculated in Block.__init__. We must ensure the loaded block's hash
            # matches this, or if we trust the saved data, explicitly set it.
            # For loading a saved state, we trust the 'hash' field from the file.
            # However, Block.__init__ already calculates and sets self.hash.
            # If block_data['hash'] differs from block.hash, it implies corruption or
            # an issue in how Block.calculate_hash works vs. how it was saved.
            # For robustness, we can assign the loaded hash, assuming the saved state was valid.
            if block.hash != block_data.get('hash'):
                print(f"Warning: Hash mismatch for loaded Block #{block.index}. Using stored hash.")
                block.hash = block_data.get('hash', block.hash) # Prefer stored hash if available
            
            blockchain_instance.chain.append(block)
        
        # If, after loading, the chain is empty (e.g., corrupted file or new/empty save file),
        # create a genesis block to ensure the blockchain is always minimally functional.
        if not blockchain_instance.chain:
            print("Warning: Loaded chain was empty or missing. Re-creating genesis block.")
            blockchain_instance.create_genesis_block()
            
        return blockchain_instance

    def save_to_file(self, filename: str = "blockchain_data.json"):
        """
        Saves the current state of the blockchain (chain, pending transactions, settings)
        to a JSON file.

        Args:
            filename (str, optional): The name of the file to save to.
                                      Defaults to "blockchain_data.json".
        """
        try:
            data_to_save = self.to_json_serializable()
            with open(filename, 'w') as f:
                # indent=4 makes the JSON file human-readable
                json.dump(data_to_save, f, indent=4)
            print(f"Blockchain state successfully saved to {filename}")
        except IOError as e:
            print(f"Error: Could not save blockchain to file '{filename}': {e}")
        except Exception as e:
            print(f"An unexpected error occurred while saving blockchain: {e}")

    @classmethod
    def load_from_file(cls, filename: str = "blockchain_data.json") -> 'Blockchain | None':
        """
        Loads the blockchain state from a specified JSON file.
        If the file doesn't exist or is invalid, it indicates that a new
        blockchain should be created.

        Args:
            filename (str, optional): The name of the file to load from.
                                      Defaults to "blockchain_data.json".

        Returns:
            Blockchain | None: A Blockchain instance populated from the file,
                               or None if loading fails (e.g., file not found,
                               corrupt data), signaling to create a new blockchain.
        """
        try:
            with open(filename, 'r') as f:
                data = json.load(f)
            print(f"Blockchain data successfully loaded from {filename}")
            return cls.from_json_serializable(data)
        except FileNotFoundError:
            print(f"Info: No saved blockchain found at '{filename}'. A new blockchain will be initialized.")
            return None
        except json.JSONDecodeError as e:
            print(f"Error: Could not decode JSON from '{filename}': {e}. A new blockchain will be initialized.")
            return None
        except IOError as e:
            print(f"Error: Could not read file '{filename}': {e}. A new blockchain will be initialized.")
            return None
        except Exception as e:
            print(f"An unexpected error occurred during loading from '{filename}': {e}. A new blockchain will be initialized.")
            return None

    def __repr__(self) -> str:
        """
        Provides a concise string representation of the Blockchain object,
        showing key statistics like the number of blocks and pending transactions.

        Returns:
            str: A string summary of the blockchain.
        """
        return (f"Blockchain(blocks={len(self.chain)}, "
                f"pending_tx={len(self.pending_transactions)}, "
                f"difficulty={self.difficulty})")

# --- Example Usage (for testing this file directly) ---
if __name__ == '__main__':
    print("--- Testing Blockchain Class with Save/Load ---")
    test_filename = "test_blockchain_data.json" # Use a test file to avoid overwriting main data

    # Scenario 1: Create new, save, load, validate
    print("\n--- SCENARIO 1: New Blockchain ---")
    bc1 = Blockchain(difficulty=2) # Lower difficulty for faster testing
    bc1.create_genesis_block() # Explicitly create genesis if not done by load_from_file
    print(bc1)

    bc1.add_transaction("Alice", "Bob", 50)
    bc1.add_transaction("Bob", "Charlie", 20)
    bc1.mine_pending_transactions("Miner1")

    bc1.add_transaction("Charlie", "Alice", 10)
    bc1.mine_pending_transactions("Miner2")

    print("\nSaving bc1...")
    bc1.save_to_file(test_filename)
    assert bc1.is_chain_valid(), "bc1 should be valid before saving."

    print("\nLoading bc2 from bc1's save file...")
    bc2 = Blockchain.load_from_file(test_filename)
    assert bc2 is not None, "bc2 should load successfully."
    print(bc2)
    assert bc2.is_chain_valid(), "bc2 should be valid after loading."
    assert len(bc1.chain) == len(bc2.chain), "Chain lengths should match after load."
    assert bc1.difficulty == bc2.difficulty, "Difficulties should match."
    assert bc1.chain[-1].hash == bc2.chain[-1].hash, "Last block hashes should match."
    print("SCENARIO 1 PASSED.")

    # Scenario 2: Load non-existent file (should create new)
    print("\n--- SCENARIO 2: Load Non-Existent File ---")
    bc3 = Blockchain.load_from_file("non_existent_file.json")
    assert bc3 is None, "Loading non-existent file should return None."
    if bc3 is None: # As expected
        bc3 = Blockchain(difficulty=1) # Create a new one as main.py would
        bc3.create_genesis_block()
    print(bc3)
    assert len(bc3.chain) == 1, "bc3 should have only a genesis block."
    print("SCENARIO 2 PASSED (created new blockchain).")

    # Clean up test file (optional)
    import os
    if os.path.exists(test_filename):
        os.remove(test_filename)
        print(f"\nCleaned up {test_filename}")