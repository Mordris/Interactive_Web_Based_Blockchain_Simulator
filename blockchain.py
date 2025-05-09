# simple_blockchain_py/blockchain.py

# Standard library imports
import time  # Used for block timestamps
import json  # Used for serializing data for hashing and saving/loading

# Local application imports
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
        # self.chain will store the sequence of Block objects
        self.chain: list[Block] = []
        # self.pending_transactions stores Transaction objects waiting to be mined
        self.pending_transactions: list[Transaction] = []
        # self.difficulty determines how hard it is to mine a block
        self.difficulty: int = int(difficulty) # Ensure it's an integer
        # self.mining_reward is the amount given to the miner of a block
        self.mining_reward: float = float(mining_reward) # Ensure it's a float
        # Note: The genesis block is not created here directly.
        # It's created by load_from_file if no file exists, or by create_genesis_block if called.

    def create_genesis_block(self):
        """
        Creates the first block in the chain (the "genesis block").
        This block is special as it has no preceding block.
        """
        print("Creating Genesis Block...")
        # Create a Block instance for the genesis block.
        # Index is 0, transactions list is empty (or could contain a special genesis transaction).
        # Timestamp is current time. Previous hash is "0" by convention. Nonce is usually 0.
        genesis_block = Block(
            index=0,
            transactions=[], # No user transactions in the genesis block for this simulation
            timestamp=time.time(),
            previous_hash="0", # Conventional placeholder for the first block
            nonce=0 # Genesis block usually has a fixed nonce or simple/no PoW
        )
        # Add the newly created genesis block to the blockchain's chain.
        self.chain.append(genesis_block)
        print(f"Genesis Block created: {genesis_block}") # Log creation

    def get_latest_block(self) -> Block | None:
        """
        Returns the most recently added block in the chain (the last block).

        Returns:
            Block | None: The last Block object in the chain, or None if the chain is empty.
        """
        # Check if the chain has any blocks
        if self.chain:
            # If not empty, return the last element of the list
            return self.chain[-1]
        else:
            # If empty, return None
            return None

    def add_transaction(self, sender: str, recipient: str, amount: float) -> int:
        """
        Creates a new transaction from the given details and adds it to the
        list of pending transactions, waiting to be mined into a block.

        Args:
            sender (str): The address or identifier of the transaction sender.
            recipient (str): The address or identifier of the transaction recipient.
            amount (float): The amount to be transferred.

        Returns:
            int: The index of the block to which this transaction will likely be added
                 (i.e., current latest block index + 1). Returns -1 on failure
                 (e.g., invalid transaction data).
        """
        try:
            # Attempt to create a Transaction object. This may raise ValueError if data is invalid.
            transaction = Transaction(sender=sender, recipient=recipient, amount=amount)
            # If successful, add the transaction to the list of pending transactions.
            self.pending_transactions.append(transaction)
            print(f"Transaction added to pending pool: {transaction}") # Log addition

            # Determine the index of the next block that will contain this transaction.
            latest_block = self.get_latest_block()
            if latest_block:
                # If there's a latest block, the next block index is current_latest + 1.
                return latest_block.index + 1
            else:
                # If the chain is somehow empty (e.g., before genesis is fully established),
                # assume the transaction will go into the first block (index 0).
                # This case should be rare if create_genesis_block is handled well.
                return 0
        except ValueError as e:
            # If Transaction creation fails (e.g., negative amount, empty sender/recipient).
            print(f"Error adding transaction: {e}") # Log the error
            return -1 # Indicate failure

    def proof_of_work(self, block: Block) -> tuple[str, float]:
        """
        Implements a simple Proof-of-Work (PoW) algorithm.
        The goal is to find a 'nonce' value for the given block such that
        the block's hash starts with a specific number of leading zeros,
        as defined by `self.difficulty`. This process is computationally intensive.

        Args:
            block (Block): The block for which to find a valid nonce and hash.

        Returns:
            tuple[str, float]: A tuple containing:
                               - The valid hash found for the block after PoW.
                               - The time taken (in seconds) to find the valid hash.
        """
        print(f"Mining block #{block.index} with difficulty {self.difficulty} (target prefix: '{'0'*self.difficulty}')...")
        # Initialize or reset the block's nonce to 0 before starting the search.
        block.nonce = 0
        
        # Record the start time to measure how long mining takes.
        start_time = time.time()

        # Calculate the initial hash of the block with nonce = 0.
        computed_hash = block.calculate_hash()
        # Define the target prefix (string of zeros) based on the current difficulty.
        target_prefix = '0' * self.difficulty

        # Loop until the computed_hash starts with the target_prefix.
        while not computed_hash.startswith(target_prefix):
            # Increment the nonce by 1.
            block.nonce += 1
            # Recalculate the block's hash with the new nonce.
            computed_hash = block.calculate_hash()
            # Optional: Print progress for very high difficulties or long mining times
            # if block.nonce % 100000 == 0 and block.nonce > 0:
            #     print(f"  ...still mining (nonce: {block.nonce}, current hash prefix: {computed_hash[:self.difficulty]})")

        # Record the end time after a valid hash is found.
        end_time = time.time()
        # Calculate the duration of the mining process.
        mining_duration = end_time - start_time

        print(f"Block successfully mined! Nonce: {block.nonce}, Hash: {computed_hash}, Time: {mining_duration:.4f} seconds")
        # CRITICAL: Update the block's actual hash attribute with the valid hash found by PoW.
        block.hash = computed_hash
        # Return both the valid hash and the time it took to find it.
        return computed_hash, mining_duration

    def mine_pending_transactions(self, mining_reward_address: str) -> tuple[Block | None, float | None]:
        """
        Mines a new block containing all transactions currently in the pending pool.
        Also includes a reward transaction for the miner.

        Args:
            mining_reward_address (str): The address to which the mining reward will be sent.

        Returns:
            tuple[Block | None, float | None]: A tuple containing:
                                               - The newly mined Block object if successful, or None.
                                               - The mining duration in seconds if successful, or None.
        """
        # Check if there are any transactions to mine.
        # If difficulty is 0, empty blocks might be allowed for testing PoW itself.
        # Otherwise, typically, we don't mine empty blocks.
        if not self.pending_transactions and self.difficulty > 0:
            print("No pending transactions to mine.")
            return None, None # Return None for both block and duration

        print(f"\nAttempting to mine new block for {len(self.pending_transactions)} pending transactions...")

        # Create the mining reward transaction.
        # 'sender="network"' signifies the reward is generated by the system, not from another user.
        reward_tx = Transaction(
            sender="network",
            recipient=mining_reward_address,
            amount=self.mining_reward
        )
        # Combine the reward transaction with the user's pending transactions.
        # The reward transaction is often placed first in the block.
        transactions_for_block_objects = [reward_tx] + self.pending_transactions

        # Get the latest block to link the new block to it.
        latest_block = self.get_latest_block()
        if not latest_block: # This should ideally not happen if genesis is handled.
            print("Error: Cannot mine. Blockchain is empty (no latest block to link to).")
            return None, None

        # Create a new Block instance for the transactions.
        new_block = Block(
            index=latest_block.index + 1, # Index is one greater than the last block.
            # Convert Transaction objects to dictionaries for storage in the Block.
            # This ensures consistent serialization for hashing via Block.calculate_hash.
            transactions=[tx.to_dict() for tx in transactions_for_block_objects],
            timestamp=time.time(), # Current time as the block's timestamp.
            previous_hash=latest_block.hash # Link to the previous block's hash.
            # Nonce will be determined by proof_of_work. Hash will also be set by PoW.
        )

        # Perform Proof-of-Work to find the valid nonce and hash for the new block.
        # This function call will update new_block.hash and new_block.nonce internally.
        _valid_hash, mining_duration = self.proof_of_work(new_block)
        # _valid_hash is returned but new_block.hash is the primary source now.

        # Add the newly mined (and now valid) block to the blockchain.
        self.chain.append(new_block)
        print(f"Block #{new_block.index} successfully mined and added to the chain.")

        # Clear the pending transactions pool as they are now included in a block.
        self.pending_transactions = []

        # Return the mined block and the duration it took to mine.
        return new_block, mining_duration

    def is_chain_valid(self) -> bool:
        """
        Validates the integrity of the entire blockchain.
        Checks data integrity, link integrity, and Proof-of-Work validity for each block.

        Returns:
            bool: True if the entire blockchain is valid, False otherwise.
        """
        print("\nValidating blockchain integrity...")
        # An empty chain (before any blocks, including genesis, are added) might be considered valid.
        if not self.chain:
            print("Blockchain is empty. Considered valid by default.")
            return True

        # --- 1. Validate the Genesis Block ---
        genesis_block = self.chain[0] # Get the first block
        # Check fundamental properties of the genesis block.
        if genesis_block.index != 0 or genesis_block.previous_hash != "0":
            print(f"Genesis block (Index {genesis_block.index}) is malformed: Index should be 0 and previous_hash '0'.")
            return False
        
        # Re-calculate genesis block hash to check for tampering.
        # Create a temporary Block instance to avoid modifying the one in the chain during the check.
        temp_genesis = Block(index=genesis_block.index, 
                             transactions=genesis_block.transactions,
                             timestamp=genesis_block.timestamp, 
                             previous_hash=genesis_block.previous_hash, 
                             nonce=genesis_block.nonce)
        if genesis_block.hash != temp_genesis.calculate_hash():
            print(f"Genesis Block (Index {genesis_block.index}) data integrity compromised!")
            print(f"  Stored hash:     {genesis_block.hash}")
            print(f"  Recalculated hash: {temp_genesis.calculate_hash()}")
            return False
        
        # Optional: Stricter PoW check for genesis if desired.
        # For this simulation, genesis PoW is often skipped or trivial.
        # If self.difficulty > 0, and genesis block is not special (e.g. all zeros hash),
        # it should also meet PoW criteria. Here, we're lenient.

        # --- 2. Validate the rest of the chain (from the second block onwards) ---
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]    # The block being validated.
            previous_block = self.chain[i-1] # The block before the current one.

            # a. Check current block's hash integrity (data tampering check).
            # Recreate a temporary block with current_block's data and stored nonce.
            temp_current_block = Block(index=current_block.index, 
                                       transactions=current_block.transactions,
                                       timestamp=current_block.timestamp, 
                                       previous_hash=current_block.previous_hash,
                                       nonce=current_block.nonce)
            if current_block.hash != temp_current_block.calculate_hash():
                print(f"Data integrity compromised at Block #{current_block.index}.")
                print(f"  Stored hash:      {current_block.hash}")
                print(f"  Recalculated hash: {temp_current_block.calculate_hash()}")
                return False

            # b. Check the chain link integrity (previous_hash matches actual previous block's hash).
            if current_block.previous_hash != previous_block.hash:
                print(f"Chain broken: Previous hash mismatch at Block #{current_block.index}.")
                print(f"  Block {current_block.index} stores previous_hash: {current_block.previous_hash}")
                print(f"  Block {previous_block.index} actual hash is:        {previous_block.hash}")
                return False

            # c. Check Proof-of-Work for the current block.
            # This check is only meaningful if difficulty is greater than 0.
            if self.difficulty > 0:
                target_prefix = '0' * self.difficulty
                if not current_block.hash.startswith(target_prefix):
                    print(f"Proof of Work invalid for Block #{current_block.index}.")
                    print(f"  Hash: {current_block.hash} (Does not start with '{target_prefix}')")
                    print(f"  Required difficulty: {self.difficulty}")
                    return False
        
        # If all checks pass for all blocks.
        print("Blockchain is valid.")
        return True

    def to_json_serializable(self) -> dict:
        """
        Converts the entire blockchain state (chain, pending transactions, settings)
        into a dictionary format that is directly serializable to JSON.

        Returns:
            dict: A dictionary representing the blockchain state.
        """
        # Convert Block objects in the chain to their dictionary representations.
        # Block.__dict__ works because Block attributes are simple types or lists of dicts.
        serializable_chain = [block.__dict__ for block in self.chain]
        # Convert Transaction objects in pending_transactions to their dictionary representations.
        serializable_pending_tx = [tx.to_dict() for tx in self.pending_transactions]

        return {
            "chain": serializable_chain,
            "pending_transactions": serializable_pending_tx,
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
        # Initialize a new Blockchain instance with difficulty and mining reward from loaded data.
        # Provide defaults if these keys are missing in the loaded data.
        loaded_difficulty = data.get('difficulty', 2)
        loaded_mining_reward = data.get('mining_reward', 100.0)
        blockchain_instance = cls(difficulty=loaded_difficulty, mining_reward=loaded_mining_reward)
        
        # Reconstruct pending Transaction objects from their dictionary representations.
        blockchain_instance.pending_transactions = [
            Transaction(sender=tx_data['sender'], recipient=tx_data['recipient'], amount=tx_data['amount'])
            for tx_data in data.get('pending_transactions', []) # Default to empty list if key missing
        ]

        # Reconstruct the chain of Block objects.
        blockchain_instance.chain = [] # Start with an empty chain before populating from data.
        for block_data in data.get('chain', []): # Default to empty list if key missing
            # Create a Block instance from the dictionary data.
            # block_data['transactions'] should already be a list of transaction dictionaries.
            block = Block(
                index=block_data['index'],
                transactions=block_data['transactions'], # These are already dicts
                timestamp=block_data['timestamp'],
                previous_hash=block_data['previous_hash'],
                nonce=block_data['nonce']
            )
            # The Block.__init__ calculates a hash. We need to ensure the loaded block
            # retains its *original, saved* hash, as that hash was part of the valid chain.
            # If block_data['hash'] is missing, Block's calculated hash will be used.
            # If it's present, we prioritize the stored hash.
            block.hash = block_data.get('hash', block.hash) 
            blockchain_instance.chain.append(block)
        
        # If, after loading, the chain is empty (e.g., corrupted file or new/empty save file),
        # create a genesis block to ensure the blockchain is always minimally functional.
        if not blockchain_instance.chain:
            print("Warning: Loaded chain was empty or missing. A new genesis block will be created.")
            blockchain_instance.create_genesis_block() # Ensure there's always at least a genesis block
            
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
            # Get the serializable dictionary representation of the blockchain.
            data_to_save = self.to_json_serializable()
            # Open the file in write mode ('w'). This will overwrite the file if it exists.
            with open(filename, 'w') as f:
                # Dump the data to the file in JSON format.
                # indent=4 makes the JSON file human-readable with pretty printing.
                json.dump(data_to_save, f, indent=4)
            print(f"Blockchain state successfully saved to {filename}")
        except IOError as e: # Catch errors related to file operations (e.g., permission denied).
            print(f"Error: Could not save blockchain to file '{filename}': {e}")
        except Exception as e: # Catch any other unexpected errors during saving.
            print(f"An unexpected error occurred while saving blockchain: {e}")

    @classmethod
    def load_from_file(cls, filename: str = "blockchain_data.json") -> 'Blockchain | None':
        """
        Loads the blockchain state from a specified JSON file.
        If the file doesn't exist or is invalid, it indicates that a new
        blockchain should be created by returning None.

        Args:
            filename (str, optional): The name of the file to load from.
                                      Defaults to "blockchain_data.json".

        Returns:
            Blockchain | None: A Blockchain instance populated from the file,
                               or None if loading fails (e.g., file not found,
                               corrupt data), signaling to create a new blockchain.
        """
        try:
            # Open the file in read mode ('r').
            with open(filename, 'r') as f:
                # Load the JSON data from the file into a Python dictionary.
                data = json.load(f)
            print(f"Blockchain data successfully loaded from {filename}")
            # Create a Blockchain instance from the loaded dictionary data.
            return cls.from_json_serializable(data)
        except FileNotFoundError:
            # If the file does not exist, inform the user and return None.
            print(f"Info: No saved blockchain found at '{filename}'. A new one will be initialized if needed.")
            return None
        except json.JSONDecodeError as e: # If the file content is not valid JSON.
            print(f"Error: Could not decode JSON from '{filename}': {e}. A new blockchain will be initialized if needed.")
            return None
        except IOError as e: # Catch other file I/O errors (e.g., permissions).
            print(f"Error: Could not read file '{filename}': {e}. A new blockchain will be initialized if needed.")
            return None
        except Exception as e: # Catch any other unexpected errors during loading.
            print(f"An unexpected error occurred during loading from '{filename}': {e}. A new blockchain will be initialized if needed.")
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
# This block helps in testing the Blockchain class independently.
if __name__ == '__main__':
    print("--- Testing Blockchain Class with Save/Load & Mining Time ---")
    # Use a distinct filename for tests to avoid interfering with main application data.
    test_filename = "test_blockchain_data.json"

    # --- SCENARIO 1: Create a new blockchain, perform operations, save, then load and verify. ---
    print("\n--- SCENARIO 1: New Blockchain Operations, Save, and Load Verification ---")
    # Initialize a new blockchain with a relatively low difficulty for faster testing.
    bc1 = Blockchain(difficulty=2)
    bc1.create_genesis_block() # Explicitly create genesis for a new chain.
    print(f"Initial state of bc1: {bc1}")

    # Add some transactions and mine a block.
    bc1.add_transaction("Alice", "Bob", 50)
    bc1.add_transaction("Bob", "Charlie", 20)
    mined_block1, duration1 = bc1.mine_pending_transactions("Miner1_Address")
    if mined_block1: print(f"  (Test Info) Block #{mined_block1.index} mined in {duration1:.4f} seconds.")

    # Add more transactions and mine another block.
    bc1.add_transaction("Charlie", "Alice", 10)
    mined_block2, duration2 = bc1.mine_pending_transactions("Miner2_Address")
    if mined_block2: print(f"  (Test Info) Block #{mined_block2.index} mined in {duration2:.4f} seconds.")

    # Save the state of bc1 to the test file.
    print("\nSaving state of bc1 to file...")
    bc1.save_to_file(test_filename)
    # Validate bc1 before assuming the saved state is good.
    assert bc1.is_chain_valid(), "Blockchain bc1 should be valid before saving."

    # Load the saved state into a new blockchain instance, bc2.
    print("\nLoading blockchain state into bc2 from bc1's save file...")
    bc2 = Blockchain.load_from_file(test_filename)
    assert bc2 is not None, "Blockchain bc2 should load successfully from file."
    print(f"State of loaded bc2: {bc2}")
    # Validate the loaded blockchain, bc2.
    assert bc2.is_chain_valid(), "Loaded blockchain bc2 should be valid."
    # Perform checks to ensure bc2 is a faithful representation of bc1.
    assert len(bc1.chain) == len(bc2.chain), "Chain lengths should match after load."
    assert bc1.difficulty == bc2.difficulty, "Difficulties should match after load."
    if bc1.chain and bc2.chain: # Ensure chains are not empty before accessing last element
        assert bc1.chain[-1].hash == bc2.chain[-1].hash, "Last block hashes should match after load."
    print("SCENARIO 1 PASSED: New, save, load, and validation successful.")

    # --- SCENARIO 2: Attempt to load from a non-existent file. ---
    print("\n--- SCENARIO 2: Attempt to Load from Non-Existent File ---")
    # This should return None, indicating failure to load.
    bc3 = Blockchain.load_from_file("this_file_should_not_exist.json")
    assert bc3 is None, "Loading a non-existent file should return None."
    # Simulate how main.py would handle this: create a new blockchain.
    if bc3 is None:
        print("  (Test Info) Simulating creation of new blockchain as load failed.")
        bc3 = Blockchain(difficulty=1) # Create a new one with default/test settings
        bc3.create_genesis_block()
    print(f"State of bc3 (newly created): {bc3}")
    assert len(bc3.chain) == 1, "Newly created bc3 should have only a genesis block."
    print("SCENARIO 2 PASSED: Correct handling of non-existent file.")

    # Clean up the test file created during SCENARIO 1.
    import os # Standard library for OS-level operations like file deletion.
    if os.path.exists(test_filename):
        os.remove(test_filename)
        print(f"\nCleaned up temporary test file: {test_filename}")