# simple_blockchain_py/blockchain.py

import time
# We need to import the Block and Transaction classes we defined earlier
from block import Block
from transaction import Transaction

class Blockchain:
    """
    Manages a chain of blocks, handles transactions, and implements
    Proof-of-Work for mining new blocks.
    """
    def __init__(self, difficulty: int = 2):
        """
        Initializes the blockchain.

        Args:
            difficulty (int): The number of leading zeros required for a valid PoW hash.
                              Higher difficulty means more computation to mine a block.
        """
        self.chain: list[Block] = []  # A list to store the blocks
        self.pending_transactions: list[Transaction] = [] # Transactions waiting to be mined
        self.difficulty: int = difficulty
        self.mining_reward: float = 100.0 # Arbitrary reward for the miner

        # Create the genesis block upon initialization
        self.create_genesis_block()

    def create_genesis_block(self):
        """
        Creates the first block in the chain (the "genesis block").
        This block has an index of 0, an empty list of transactions (or a placeholder),
        and a conventional previous_hash (e.g., "0").
        """
        print("Creating Genesis Block...")
        genesis_block = Block(
            index=0,
            transactions=[], # Genesis block often has no transactions or a special one
            timestamp=time.time(),
            previous_hash="0" # Conventional previous hash for genesis
            # Nonce will be calculated if PoW is applied to genesis, or default to 0
        )
        # For simplicity, let's not require PoW for the genesis block initially,
        # or we can make its PoW very easy.
        # If we want PoW for genesis: self.proof_of_work(genesis_block)
        # Or, just ensure its hash is calculated:
        # genesis_block.hash = genesis_block.calculate_hash() # Already done in Block.__init__

        self.chain.append(genesis_block)
        print(f"Genesis Block created: {genesis_block}")

    def get_latest_block(self) -> Block:
        """
        Returns the most recently added block in the chain.
        """
        if not self.chain:
            # This case should ideally not happen if genesis block is always created
            raise Exception("Blockchain is empty! No latest block.")
        return self.chain[-1]

    def add_transaction(self, sender: str, recipient: str, amount: float) -> int:
        """
        Creates a new transaction and adds it to the list of pending transactions.

        Args:
            sender (str): The address of the sender.
            recipient (str): The address of the recipient.
            amount (float): The amount to transfer.

        Returns:
            int: The index of the block to which this transaction will be added (once mined).
        """
        if not sender or not recipient or amount <= 0:
            print("Invalid transaction data.")
            # Potentially raise an error or return a specific indicator
            return -1 # Indicate failure or next block index as error

        transaction = Transaction(sender=sender, recipient=recipient, amount=amount)
        self.pending_transactions.append(transaction)
        print(f"Transaction added: {transaction}")

        # Return the index of the next block that will include this transaction
        return self.get_latest_block().index + 1

    def proof_of_work(self, block: Block) -> str:
        """
        Implements a simple Proof-of-Work algorithm.
        It tries different nonce values until a hash is found that
        starts with a certain number of leading zeros (defined by `self.difficulty`).

        Args:
            block (Block): The block to find a valid nonce for.

        Returns:
            str: The valid hash found for the block.
        """
        print(f"Mining block {block.index} with difficulty {self.difficulty}...")
        block.nonce = 0 # Reset nonce before starting
        computed_hash = block.calculate_hash()
        target_prefix = '0' * self.difficulty

        while not computed_hash.startswith(target_prefix):
            block.nonce += 1
            computed_hash = block.calculate_hash()
            # Optional: Print progress for very hard difficulties
            # if block.nonce % 100000 == 0:
            #     print(f"  Still mining... (nonce: {block.nonce}, hash: {computed_hash})")


        print(f"Block mined! Nonce: {block.nonce}, Hash: {computed_hash}")
        block.hash = computed_hash # Important: update the block's hash with the valid one
        return computed_hash

    def mine_pending_transactions(self, mining_reward_address: str) -> Block | None:
        """
        Mines a new block containing all pending transactions.
        This involves:
        1. Creating a "reward" transaction for the miner.
        2. Creating a new block with the pending transactions.
        3. Performing Proof-of-Work on the new block.
        4. Adding the mined block to the chain.
        5. Clearing the list of pending transactions.

        Args:
            mining_reward_address (str): The address to send the mining reward to.

        Returns:
            Block | None: The newly mined block, or None if no transactions to mine.
        """
        if not self.pending_transactions and self.difficulty > 0: # Don't mine empty blocks unless difficulty is 0 (testing)
            print("No pending transactions to mine.")
            return None

        print(f"\nMining new block for {len(self.pending_transactions)} pending transactions...")

        # Create a reward transaction for the miner
        # This is a conceptual reward, not tied to actual balances in this simple simulation
        reward_transaction = Transaction(
            sender="network", # Or "0000" or some system identifier
            recipient=mining_reward_address,
            amount=self.mining_reward
        )
        # Add the reward transaction to the list of transactions for this block
        # It's common to put it as the first transaction
        transactions_for_new_block = [reward_transaction] + self.pending_transactions

        latest_block = self.get_latest_block()
        new_block = Block(
            index=latest_block.index + 1,
            # Convert Transaction objects to dictionaries for storage in the block,
            # as our Block.calculate_hash expects a list of serializable items.
            transactions=[tx.to_dict() for tx in transactions_for_new_block],
            timestamp=time.time(),
            previous_hash=latest_block.hash
            # Nonce will be found by proof_of_work
        )

        # Perform Proof-of-Work
        self.proof_of_work(new_block) # This will set new_block.hash

        # Add the newly mined block to the chain
        self.chain.append(new_block)
        print(f"Block #{new_block.index} successfully mined and added to the chain.")

        # Clear the pending transactions list
        self.pending_transactions = []

        return new_block

    def is_chain_valid(self) -> bool:
        """
        Validates the integrity of the blockchain.
        Checks:
        1. If each block's stored hash is correct (recalculating it).
        2. If each block's `previous_hash` correctly points to the hash of the previous block.
        3. (Optional for P1, but good) If the PoW condition is met for each block's hash.
        """
        print("\nValidating blockchain integrity...")
        for i in range(1, len(self.chain)): # Start from the second block (index 1)
            current_block = self.chain[i]
            previous_block = self.chain[i-1]

            # 1. Check if the stored hash of the current block is correct
            #    We need to temporarily set the nonce of current_block to its stored nonce
            #    before recalculating, as calculate_hash uses self.nonce
            #    Alternatively, Block.calculate_hash could take nonce as an argument
            #    For simplicity here, we rely on Block calculating its hash correctly on init
            #    and PoW updating it. So, we re-calculate it as if it were being created.
            #    Let's create a temporary block instance for recalculation to avoid side effects.
            
            # Create a new Block instance with the same data to recalculate its hash
            # without modifying the original block's hash in the chain during validation.
            # This is crucial because calculate_hash in Block might modify self.hash internally
            # if not designed carefully (though our current Block sets hash in __init__).
            # For robust validation, it's best to recalculate from scratch.
            
            temp_block_for_hash_check = Block(
                index=current_block.index,
                transactions=current_block.transactions, # Assuming these are already dicts
                timestamp=current_block.timestamp,
                previous_hash=current_block.previous_hash,
                nonce=current_block.nonce # Use the nonce stored in the block
            )

            if current_block.hash != temp_block_for_hash_check.calculate_hash():
                print(f"Data integrity compromised at Block #{current_block.index}.")
                print(f"  Stored hash:      {current_block.hash}")
                print(f"  Recalculated hash: {temp_block_for_hash_check.calculate_hash()}")
                return False

            # 2. Check if the previous_hash link is correct
            if current_block.previous_hash != previous_block.hash:
                print(f"Chain broken: Previous hash mismatch at Block #{current_block.index}.")
                print(f"  Block {current_block.index} previous_hash: {current_block.previous_hash}")
                print(f"  Block {previous_block.index} hash:          {previous_block.hash}")
                return False

            # 3. (Optional but good) Check if PoW condition is met for each block's hash
            target_prefix = '0' * self.difficulty
            if not current_block.hash.startswith(target_prefix) and self.difficulty > 0:
                # Genesis block might be an exception if not mined with PoW
                if current_block.index == 0 and current_block.previous_hash == "0": # common genesis check
                    pass # Allow genesis block without PoW check if intended
                else:
                    print(f"Proof of Work invalid for Block #{current_block.index}.")
                    print(f"  Hash: {current_block.hash} (Difficulty: {self.difficulty})")
                    return False
        
        # Also check genesis block's hash integrity (if not covered by the loop)
        if self.chain:
            genesis_block = self.chain[0]
            temp_genesis_for_hash_check = Block(
                index=genesis_block.index,
                transactions=genesis_block.transactions,
                timestamp=genesis_block.timestamp,
                previous_hash=genesis_block.previous_hash,
                nonce=genesis_block.nonce
            )
            if genesis_block.hash != temp_genesis_for_hash_check.calculate_hash():
                print(f"Data integrity compromised at Genesis Block #{genesis_block.index}.")
                return False


        print("Blockchain is valid.")
        return True

    def __repr__(self) -> str:
        """
        Provides a string representation of the blockchain, showing basic info.
        """
        return f"Blockchain(blocks={len(self.chain)}, pending_tx={len(self.pending_transactions)}, difficulty={self.difficulty})"


if __name__ == '__main__':
    # Example Usage for testing the Blockchain class directly
    print("--- Initializing Simple Blockchain ---")
    my_blockchain = Blockchain(difficulty=3) # Difficulty 3 means hash must start with "000"
    print(my_blockchain)
    print(f"Latest block after init: {my_blockchain.get_latest_block()}")

    print("\n--- Adding Transactions ---")
    my_blockchain.add_transaction(sender="Alice", recipient="Bob", amount=50.0)
    my_blockchain.add_transaction(sender="Bob", recipient="Charlie", amount=25.5)
    print(f"Pending transactions: {len(my_blockchain.pending_transactions)}")
    for tx in my_blockchain.pending_transactions:
        print(f"  - {tx}")

    print("\n--- Mining Pending Transactions (Block 1) ---")
    miner1_address = "miner-node-1"
    mined_block1 = my_blockchain.mine_pending_transactions(mining_reward_address=miner1_address)
    if mined_block1:
        print(f"Mined Block 1: {mined_block1}")
    print(f"Pending transactions after mining: {len(my_blockchain.pending_transactions)}")
    print(my_blockchain)


    print("\n--- Adding More Transactions ---")
    my_blockchain.add_transaction(sender="Charlie", recipient="David", amount=10.0)
    my_blockchain.add_transaction(sender="David", recipient="Alice", amount=5.0)

    print("\n--- Mining Pending Transactions (Block 2) ---")
    miner2_address = "miner-node-2"
    mined_block2 = my_blockchain.mine_pending_transactions(mining_reward_address=miner2_address)
    if mined_block2:
        print(f"Mined Block 2: {mined_block2}")
    print(my_blockchain)

    print("\n--- Validating Chain ---")
    is_valid = my_blockchain.is_chain_valid()
    print(f"Is the blockchain valid? {is_valid}")

    # --- Test Tampering (Optional) ---
    if len(my_blockchain.chain) > 1:
        print("\n--- Simulating Tampering ---")
        # Tamper with a transaction in a mined block
        # IMPORTANT: This modification is in-memory and only for testing validation.
        # Real blockchains are immutable due to distribution and consensus.
        original_transaction_amount = my_blockchain.chain[1].transactions[1]['amount'] # Assuming second tx is user tx
        print(f"Original transaction in Block 1: {my_blockchain.chain[1].transactions[1]}")
        my_blockchain.chain[1].transactions[1]['amount'] = 10000.0 # Alice tries to give Bob much more
        print(f"Tampered transaction in Block 1: {my_blockchain.chain[1].transactions[1]}")
        
        print("\n--- Re-validating Chain After Tampering ---")
        is_valid_after_tamper = my_blockchain.is_chain_valid()
        print(f"Is the blockchain valid after tampering? {is_valid_after_tamper}")
        assert not is_valid_after_tamper, "Chain validation should detect tampering!"

        # Restore for further tests if needed, or just note the test is done
        my_blockchain.chain[1].transactions[1]['amount'] = original_transaction_amount


    print("\n--- Final Blockchain State ---")
    for i, block in enumerate(my_blockchain.chain):
        print(f"\nBlock #{block.index} (Hash: {block.hash})")
        print(f"  Timestamp: {block.timestamp}")
        print(f"  Nonce: {block.nonce}")
        print(f"  Previous Hash: {block.previous_hash}")
        print(f"  Transactions ({len(block.transactions)}):")
        for tx_dict in block.transactions:
            # tx_obj = Transaction(sender=tx_dict['sender'], recipient=tx_dict['recipient'], amount=tx_dict['amount'])
            print(f"    - {tx_dict}") # Print the dictionary representation