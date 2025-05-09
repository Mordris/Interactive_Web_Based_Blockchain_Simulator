# simple_blockchain_py/main.py

# Local application import
from blockchain import Blockchain # Import the core Blockchain class and its logic

def print_blockchain_details(chain_instance: Blockchain):
    """
    Helper function to print the current state of the blockchain
    in a detailed and readable format to the console.

    Args:
        chain_instance (Blockchain): The Blockchain object to display.
    """
    # Print a header for the blockchain display
    print("\n" + "="*10 + " Current Blockchain State " + "="*10)
    # Check if the blockchain has any blocks
    if not chain_instance.chain:
        print("The blockchain is currently empty (no blocks have been created or loaded).")
        return # Exit the function if no blocks

    # Print overall statistics
    print(f"Total blocks in chain: {len(chain_instance.chain)}")
    print(f"Current mining difficulty: {chain_instance.difficulty}")
    print(f"Standard mining reward: {chain_instance.mining_reward}")

    # Iterate through each block in the chain and print its details
    for i, block in enumerate(chain_instance.chain):
        print(f"\n--- Block #{block.index} ---") # Block number (index)
        # Format timestamp to be more human-readable (integer part)
        print(f"  Timestamp: {block.timestamp:.0f} (Unix Epoch Seconds)")
        print(f"  Nonce: {block.nonce}") # The nonce found during PoW
        print(f"  Hash: {block.hash}") # The block's own calculated hash
        print(f"  Previous Hash: {block.previous_hash}") # Link to the previous block
        print(f"  Transactions ({len(block.transactions)}):") # Number of transactions in the block
        if block.transactions:
            # If there are transactions, iterate and print each one's details
            for tx_num, tx_dict in enumerate(block.transactions):
                print(f"    {tx_num+1}. From: {tx_dict['sender']}, To: {tx_dict['recipient']}, Amount: {tx_dict['amount']}")
        else:
            # If no transactions in this block (e.g., genesis or an empty mined block)
            print("    - No transactions in this block.")
    # Print a footer for the blockchain display
    print("="*10 + " End of Blockchain State " + "="*10)

def main_cli():
    """
    Main function to run the Command-Line Interface (CLI)
    for interacting with the blockchain simulation.
    Handles user input and calls appropriate Blockchain methods.
    """
    print("--- Simple Blockchain Simulation CLI ---")
    
    # Define the default filename for saving and loading blockchain data
    blockchain_data_filename = "blockchain_data.json"
    
    # Attempt to load an existing blockchain state from the file
    print(f"\nAttempting to load blockchain data from '{blockchain_data_filename}'...")
    my_blockchain = Blockchain.load_from_file(blockchain_data_filename)

    # If loading failed (e.g., file not found, corrupt data), my_blockchain will be None.
    # In this case, initialize a new blockchain.
    if my_blockchain is None:
        print("\nNo existing blockchain found or an error occurred during loading.")
        # Loop to get valid difficulty input from the user for the new blockchain
        while True:
            try:
                difficulty_str = input("Enter desired blockchain mining difficulty (e.g., 2, 3, 4 - higher is harder): ").strip()
                # Handle empty input by defaulting or re-prompting
                if not difficulty_str:
                    print("Difficulty cannot be empty. Please enter a number (e.g., 2).")
                    continue # Re-prompt
                difficulty = int(difficulty_str) # Convert input to integer
                if difficulty < 1: # Difficulty must be at least 1 for PoW to be meaningful
                    print("Difficulty must be at least 1 for PoW to have an effect. Please try again.")
                else:
                    break # Valid difficulty entered, exit loop
            except ValueError: # Handle cases where input is not a valid integer
                print("Invalid input. Difficulty must be an integer (e.g., 2).")
        
        # Create a new Blockchain instance with the user-defined difficulty
        my_blockchain = Blockchain(difficulty=difficulty)
        # Create the genesis block for this new chain
        my_blockchain.create_genesis_block()
        print(f"\nNew blockchain initialized with difficulty {my_blockchain.difficulty}.")
        # The create_genesis_block method already prints a confirmation.
    else:
        # If blockchain was loaded successfully
        print(f"\nExisting blockchain successfully loaded from '{blockchain_data_filename}'.")
        print(f"  Current state: {my_blockchain}") # Uses Blockchain.__repr__ for summary

    # Define a default address for miner rewards in this CLI simulation
    default_miner_address = "cli-miner-rewards-address"
    print(f"Default miner reward address set to: {default_miner_address}")

    # Main interaction loop for the CLI menu
    while True:
        # Print the menu options
        print("\n" + "-"*15 + " Blockchain CLI Menu " + "-"*15)
        print("1. Add a new transaction")
        print("2. Mine pending transactions")
        print("3. Display the full blockchain")
        print("4. Validate the blockchain")
        print("5. View pending transactions")
        print("6. Save blockchain to file")
        print("7. Exit")
        print("-"*47) # Separator line

        # Get user's choice
        choice = input("Enter your choice (1-7): ").strip()

        # --- Handle option 1: Add a new transaction ---
        if choice == '1':
            try:
                print("\n--- Add New Transaction ---")
                sender = input("  Enter sender address: ").strip()
                recipient = input("  Enter recipient address: ").strip()
                amount_str = input("  Enter transaction amount: ").strip()
                amount = float(amount_str) # Convert amount to float; can raise ValueError
                
                # Call the blockchain method to add the transaction
                # This method internally calls Transaction.__init__ which validates input.
                next_block_idx = my_blockchain.add_transaction(sender, recipient, amount)
                # Check if the transaction was added successfully (add_transaction returns -1 on failure)
                if next_block_idx != -1 :
                    print(f"  Transaction successfully added to pending pool. Expected in Block #{next_block_idx} after mining.")
                # else: The add_transaction or Transaction constructor already printed an error.
            except ValueError as ve: # Catch errors from float conversion or Transaction validation
                print(f"  Error: Invalid transaction input - {ve}")
            except Exception as e: # Catch any other unexpected errors
                print(f"  An unexpected error occurred while adding transaction: {e}")

        # --- Handle option 2: Mine pending transactions ---
        elif choice == '2':
            print(f"\n--- Mine Pending Transactions ---")
            print(f"Attempting to mine. Rewards will go to: {default_miner_address}")
            # Check if there are transactions to mine, especially if difficulty makes empty blocks pointless
            if not my_blockchain.pending_transactions and my_blockchain.difficulty > 0:
                print("  No transactions currently in the pending pool to mine. Add some transactions first.")
            else:
                # Call the mining method, which returns the mined block and duration
                mined_block, mining_duration = my_blockchain.mine_pending_transactions(mining_reward_address=default_miner_address)
                
                if mined_block: # If a block was successfully mined
                    print(f"  Successfully mined new Block #{mined_block.index}!")
                    print(f"    Hash: {mined_block.hash}")
                    print(f"    Nonce: {mined_block.nonce}")
                    if mining_duration is not None: # Display mining time if available
                        print(f"    Mining Time: {mining_duration:.4f} seconds")
                # else: mine_pending_transactions would have printed specific reasons for not mining (e.g., no txs)

        # --- Handle option 3: Display the full blockchain ---
        elif choice == '3':
            print_blockchain_details(my_blockchain)

        # --- Handle option 4: Validate the blockchain ---
        elif choice == '4':
            print("\n--- Validate Blockchain ---")
            is_valid = my_blockchain.is_chain_valid() # Call the validation method
            if is_valid:
                print("Blockchain integrity check result: VALID")
            else:
                # The is_chain_valid method itself prints details about where validation failed.
                print("Blockchain integrity check result: INVALID (see console output above for details)")

        # --- Handle option 5: View pending transactions ---
        elif choice == '5':
            print("\n--- Current Pending Transactions ---")
            if my_blockchain.pending_transactions:
                # Iterate and print each pending transaction using its __repr__ method
                for i, tx in enumerate(my_blockchain.pending_transactions):
                    print(f"  {i+1}. {tx}")
            else:
                print("  No transactions currently pending.")
            print("----------------------------------")
        
        # --- Handle option 6: Save blockchain to file ---
        elif choice == '6':
            print("\n--- Save Blockchain ---")
            my_blockchain.save_to_file(blockchain_data_filename) # Call save method

        # --- Handle option 7: Exit ---
        elif choice == '7':
            print("\n--- Exit Application ---")
            # Ask user if they want to save before exiting
            save_on_exit = input("Save current blockchain state before exiting? (y/n, default: n): ").strip().lower()
            if save_on_exit == 'y':
                my_blockchain.save_to_file(blockchain_data_filename)
            print("Exiting Simple Blockchain CLI. Goodbye!")
            break # Exit the main while loop, terminating the program
        
        # --- Handle invalid menu choice ---
        else:
            print("Invalid choice. Please enter a number between 1 and 7.")

# Standard Python entry point: ensures main_cli() is called only when the script is executed directly.
if __name__ == "__main__":
    main_cli()