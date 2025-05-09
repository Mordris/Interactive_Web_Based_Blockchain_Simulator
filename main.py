# simple_blockchain_py/main.py

from blockchain import Blockchain # Import your Blockchain class and related logic

def print_blockchain_details(chain_instance: Blockchain):
    """
    Helper function to print the current state of the blockchain
    in a readable format.
    """
    print("\n" + "="*10 + " Current Blockchain State " + "="*10)
    if not chain_instance.chain:
        print("The blockchain is empty (no blocks, not even genesis).")
        return

    print(f"Total blocks: {len(chain_instance.chain)}")
    print(f"Current difficulty: {chain_instance.difficulty}")
    print(f"Mining reward: {chain_instance.mining_reward}")

    for i, block in enumerate(chain_instance.chain):
        print(f"\n--- Block #{block.index} ---")
        print(f"  Timestamp: {block.timestamp:.0f} (Unix)") # Format timestamp
        print(f"  Nonce: {block.nonce}")
        print(f"  Hash: {block.hash}")
        print(f"  Previous Hash: {block.previous_hash}")
        print(f"  Transactions ({len(block.transactions)}):")
        if block.transactions:
            for tx_num, tx_dict in enumerate(block.transactions):
                print(f"    {tx_num+1}. From: {tx_dict['sender']}, To: {tx_dict['recipient']}, Amount: {tx_dict['amount']}")
        else:
            print("    - No transactions in this block.")
    print("="*10 + " End of Blockchain State " + "="*10)

def main_cli():
    """
    Main function to run the Command-Line Interface (CLI)
    for interacting with the blockchain simulation.
    """
    print("--- Simple Blockchain Simulation CLI ---")
    
    blockchain_data_filename = "blockchain_data.json" # Default filename for persistence
    
    # Attempt to load an existing blockchain from file
    my_blockchain = Blockchain.load_from_file(blockchain_data_filename)

    if my_blockchain is None:
        # If loading failed or file not found, initialize a new blockchain
        print("\nNo existing blockchain found or loading failed.")
        while True:
            try:
                difficulty_str = input("Enter desired blockchain difficulty (e.g., 2, 3, 4 - higher is harder): ")
                difficulty = int(difficulty_str)
                if difficulty < 1: # Difficulty must be at least 1 for PoW to be meaningful
                    print("Difficulty must be at least 1. Please try again.")
                else:
                    break
            except ValueError:
                print("Invalid input. Difficulty must be an integer.")
        
        my_blockchain = Blockchain(difficulty=difficulty)
        my_blockchain.create_genesis_block() # Create the first block for the new chain
        print(f"\nNew blockchain initialized with difficulty {my_blockchain.difficulty}.")
        print(f"Genesis block created: {my_blockchain.get_latest_block()}")
    else:
        print(f"\nExisting blockchain successfully loaded from '{blockchain_data_filename}'.")
        print(f"  Current difficulty: {my_blockchain.difficulty}")
        print(f"  Number of blocks: {len(my_blockchain.chain)}")


    # A default miner address for simplicity in the CLI.
    # In a real system, the miner running the software would use their own address.
    default_miner_address = "cli-miner-rewards"
    print(f"Default miner reward address: {default_miner_address}")

    # Main interaction loop
    while True:
        print("\n" + "-"*15 + " Blockchain CLI Menu " + "-"*15)
        print("1. Add a new transaction")
        print("2. Mine pending transactions")
        print("3. Display the full blockchain")
        print("4. Validate the blockchain")
        print("5. View pending transactions")
        print("6. Save blockchain to file")
        print("7. Exit")
        print("-"*47)

        choice = input("Enter your choice (1-7): ").strip()

        if choice == '1': # Add a new transaction
            try:
                sender = input("  Enter sender address: ").strip()
                recipient = input("  Enter recipient address: ").strip()
                amount_str = input("  Enter transaction amount: ").strip()
                amount = float(amount_str) # Convert to float, can raise ValueError
                
                # add_transaction now includes basic validation from Transaction class
                next_block_idx = my_blockchain.add_transaction(sender, recipient, amount)
                if next_block_idx != -1 : # Check if transaction was successfully added
                    print(f"  Transaction added to pending pool. Expected in Block #{next_block_idx}.")
                # else: add_transaction already prints error message from Transaction init
            except ValueError as ve: # Catches float conversion error or Transaction init error
                print(f"  Error: Invalid transaction input - {ve}")
            except Exception as e: # Catch any other unexpected errors
                print(f"  An unexpected error occurred: {e}")

        elif choice == '2': # Mine pending transactions
            print(f"\nAttempting to mine pending transactions. Rewards to: {default_miner_address}")
            if not my_blockchain.pending_transactions and my_blockchain.difficulty > 0:
                print("  No transactions currently in the pending pool to mine.")
            else:
                mined_block = my_blockchain.mine_pending_transactions(mining_reward_address=default_miner_address)
                if mined_block:
                    print(f"  Successfully mined new Block #{mined_block.index}!")
                    print(f"    Hash: {mined_block.hash}")
                    print(f"    Nonce: {mined_block.nonce}")
                # else: mine_pending_transactions would have printed specific reasons

        elif choice == '3': # Display the blockchain
            print_blockchain_details(my_blockchain)

        elif choice == '4': # Validate the blockchain
            is_valid = my_blockchain.is_chain_valid()
            if is_valid:
                print("Blockchain integrity check: VALID")
            else:
                print("Blockchain integrity check: INVALID (see console for details where validation failed)")

        elif choice == '5': # View pending transactions
            print("\n--- Current Pending Transactions ---")
            if my_blockchain.pending_transactions:
                for i, tx in enumerate(my_blockchain.pending_transactions):
                    print(f"  {i+1}. From: {tx.sender}, To: {tx.recipient}, Amount: {tx.amount}")
            else:
                print("  No transactions currently pending.")
            print("----------------------------------")
        
        elif choice == '6': # Save blockchain to file
            my_blockchain.save_to_file(blockchain_data_filename)

        elif choice == '7': # Exit
            save_on_exit = input("Save blockchain before exiting? (y/n, default: n): ").strip().lower()
            if save_on_exit == 'y':
                my_blockchain.save_to_file(blockchain_data_filename)
            print("Exiting Simple Blockchain CLI. Goodbye!")
            break
        else:
            print("Invalid choice. Please enter a number between 1 and 7.")

# Entry point for the CLI application
if __name__ == "__main__":
    main_cli()