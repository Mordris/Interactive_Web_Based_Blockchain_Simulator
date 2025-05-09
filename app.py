from flask import Flask, render_template, jsonify, request
from blockchain import Blockchain
import json

app = Flask(__name__)
blockchain = None

def init_blockchain():
    global blockchain
    try:
        blockchain = Blockchain.load_from_file()
        if blockchain is None:
            blockchain = Blockchain(difficulty=2)
            blockchain.create_genesis_block()
        print(f"Blockchain initialized: {blockchain}")
    except Exception as e:
        print(f"Error initializing blockchain: {e}")
        blockchain = Blockchain(difficulty=2)
        blockchain.create_genesis_block()

# Initialize blockchain immediately
init_blockchain()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/blockchain/create', methods=['POST'])
def create_blockchain():
    global blockchain
    data = request.json
    try:
        difficulty = int(data.get('difficulty', 2))
        mining_reward = float(data.get('mining_reward', 100.0))
        
        # Validate inputs
        if difficulty < 1 or difficulty > 6:
            return jsonify({'success': False, 'error': 'Difficulty must be between 1 and 6'}), 400
        if mining_reward <= 0:
            return jsonify({'success': False, 'error': 'Mining reward must be positive'}), 400
        
        # Create new blockchain
        blockchain = Blockchain(difficulty=difficulty, mining_reward=mining_reward)
        blockchain.create_genesis_block()
        blockchain.save_to_file()
        
        return jsonify({
            'success': True,
            'message': f'New blockchain created with difficulty {difficulty} and mining reward {mining_reward}'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/blockchain/status')
def get_blockchain_status():
    if blockchain is None:
        init_blockchain()
    print("DEBUG: Blockchain status - difficulty:", blockchain.difficulty)
    return jsonify({
        'blocks': len(blockchain.chain),
        'pending_transactions': len(blockchain.pending_transactions),
        'difficulty': blockchain.difficulty,
        'mining_reward': blockchain.mining_reward
    })

@app.route('/api/blockchain/blocks')
def get_blocks():
    blocks = []
    for block in blockchain.chain:
        blocks.append({
            'index': block.index,
            'timestamp': block.timestamp,
            'transactions': block.transactions,
            'previous_hash': block.previous_hash,
            'hash': block.hash,
            'nonce': block.nonce
        })
    return jsonify(blocks)

@app.route('/api/blockchain/pending-transactions')
def get_pending_transactions():
    return jsonify([tx.to_dict() for tx in blockchain.pending_transactions])

@app.route('/api/blockchain/add-transaction', methods=['POST'])
def add_transaction():
    data = request.json
    try:
        next_block_idx = blockchain.add_transaction(
            sender=data['sender'],
            recipient=data['recipient'],
            amount=float(data['amount'])
        )
        return jsonify({'success': True, 'next_block_index': next_block_idx})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/blockchain/mine', methods=['POST'])
def mine_block():
    data = request.json
    try:
        block, duration = blockchain.mine_pending_transactions(data['miner_address'])
        if block:
            return jsonify({
                'success': True,
                'block': {
                    'index': block.index,
                    'hash': block.hash,
                    'nonce': block.nonce,
                    'timestamp': block.timestamp
                },
                'mining_duration': duration
            })
        return jsonify({'success': False, 'error': 'No transactions to mine'})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/api/blockchain/validate')
def validate_chain():
    is_valid = blockchain.is_chain_valid()
    return jsonify({'valid': is_valid})

@app.route('/api/blockchain/save')
def save_blockchain():
    try:
        blockchain.save_to_file()
        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True) 