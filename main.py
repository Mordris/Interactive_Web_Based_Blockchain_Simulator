# simple_blockchain_py/main.py

from blockchain import Blockchain # Import your Blockchain class

def print_blockchain(chain_instance: Blockchain):
    """Helper function to print the blockchain in a readable format."""
    print("\n----- Current Blockchain State -----")
    if not chain_instance.chain:
        print("The blockchain is empty.")
        return

    for i, block in enumerate(chain_instance.chain):
        print(f"\nBlock #{block.index} (Hash: {block.hash})")
        print(f"  Timestamp: {block.timestamp}")
        print(f"  Nonce: {block.nonce}")
        print(f"  Previous Hash: {block.previous_hash}")
        print(f"  Transactions ({len(block.transactions)}):")
        if block.transactions:
            for tx_dict in block.transactions:
                # Assuming tx_dict is {'sender': ..., 'recipient': ..., 'amount': ...}
                print(f"    - From: {tx_dict['sender']}, To: {tx_dict['recipient']}, Amount: {tx_dict['amount']}")
        else:
            print("    - No transactions in this block.")
    print("----- End of Blockchain -----")

def main():
    """
    Main function to run the CLI for the blockchain simulation.
    """
    print("--- Simple Blockchain CLI Initializing ---")
    try:
        difficulty = int(input("Enter blockchain difficulty (e.g., 2, 3, 4 - higher is harder): "))
        if difficulty < 1:
            print("Difficulty must be at least 1. Defaulting to 2.")
            difficulty = 2
    except ValueError:
        print("Invalid input for difficulty. Defaulting to 2.")
        difficulty = 2

    my_blockchain = Blockchain(difficulty=difficulty)
    print(f"Blockchain initialized with difficulty {my_blockchain.difficulty}.")
    print(f"Genesis block: {my_blockchain.get_latest_block()}")

    # A default miner address for simplicity in the CLI
    # In a real system, the miner running the software would use their own address.
    default_miner_address = "cli-miner-reward-address"
    print(f"Default miner reward address set to: {default_miner_address}")


    while True:
        print("\nBlockchain CLI Menu:")
        print("1. Add a new transaction")
        print("2. Mine pending transactions")
        print("3. Display the blockchain")
        print("4. Validate the blockchain")
        print("5. View pending transactions")
        print("6. Exit")

        choice = input("Enter your choice (1-6): ")

        if choice == '1':
            try:
                sender = input("Enter sender address: ")
                recipient = input("Enter recipient address: ")
                amount_str = input("Enter amount: ")
                amount = float(amount_str)
                if amount <= 0:
                    print("Amount must be positive.")
                    continue
                
                next_block_index = my_blockchain.add_transaction(sender, recipient, amount)
                if next_block_index != -1: # Check if add_transaction indicated success
                    print(f"Transaction added. It will be included in Block #{next_block_index} once mined.")
                else:
                    print("Failed to add transaction (check console for details if any).")

            except ValueError:
                print("Invalid amount. Please enter a number.")
            except Exception as e:
                print(f"An error occurred while adding transaction: {e}")

        elif choice == '2':
            print(f"\nMining pending transactions. Rewards will go to: {default_miner_address}")
            if not my_blockchain.pending_transactions:
                print("No transactions to mine. Add some transactions first or try mining (empty blocks allowed if difficulty is 0).")
                # Allow mining empty blocks if difficulty is 0 (for testing PoW itself)
                # or if specifically intended. For now, we assume we usually want txs.
                # if my_blockchain.difficulty > 0:
                #    continue 
            
            mined_block = my_blockchain.mine_pending_transactions(mining_reward_address=default_miner_address)
            if mined_block:
                print(f"Successfully mined Block #{mined_block.index}!")
                print(f"  Hash: {mined_block.hash}")
                print(f"  Nonce: {mined_block.nonce}")
            # else:
                # mine_pending_transactions already prints if no transactions or other issues.
                # print("Mining did not result in a new block (check logs).")


        elif choice == '3':
            print_blockchain(my_blockchain)

        elif choice == '4':
            is_valid = my_blockchain.is_chain_valid()
            if is_valid:
                print("Blockchain integrity: VALID")
            else:
                print("Blockchain integrity: INVALID (check console for details)")

        elif choice == '5':
            print("\n--- Pending Transactions ---")
            if my_blockchain.pending_transactions:
                for i, tx in enumerate(my_blockchain.pending_transactions):
                    print(f"{i+1}. From: {tx.sender}, To: {tx.recipient}, Amount: {tx.amount}")
            else:
                print("No pending transactions.")
            print("--------------------------")
        
        elif choice == '6':
            print("Exiting Blockchain CLI. Goodbye!")
            break
        else:
            print("Invalid choice. Please enter a number between 1 and 6.")

if __name__ == "__main__":
    main()