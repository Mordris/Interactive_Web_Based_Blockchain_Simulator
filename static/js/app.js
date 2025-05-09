// Initialize toast notifications
const toast = new bootstrap.Toast(document.getElementById('toast'));

// Store last known values to prevent unnecessary updates
let lastKnownStatus = {
    blocks: 0,
    pending_transactions: 0,
    difficulty: 0,
    mining_reward: 0
};

// Show notification
function showNotification(message, isError = false) {
    const toastElement = document.getElementById('toast');
    const toastBody = toastElement.querySelector('.toast-body');
    const toastHeader = toastElement.querySelector('.toast-header');
    
    toastBody.textContent = message;
    toastHeader.className = 'toast-header ' + (isError ? 'bg-danger text-white' : 'bg-success text-white');
    toast.show();
}

// Format timestamp
function formatTimestamp(timestamp) {
    return new Date(timestamp * 1000).toLocaleString();
}

// Format hash for display
function formatHash(hash) {
    return hash.substring(0, 10) + '...' + hash.substring(hash.length - 10);
}

// Update blockchain status with animation
async function updateStatus() {
    try {
        const response = await fetch('/api/blockchain/status');
        const data = await response.json();
        
        // Only update if values have changed
        if (data.blocks !== lastKnownStatus.blocks) {
            animateNumberChange('block-count', data.blocks);
            lastKnownStatus.blocks = data.blocks;
        }
        
        if (data.pending_transactions !== lastKnownStatus.pending_transactions) {
            animateNumberChange('pending-tx-count', data.pending_transactions);
            lastKnownStatus.pending_transactions = data.pending_transactions;
        }
        
        if (data.difficulty !== lastKnownStatus.difficulty) {
            animateNumberChange('difficulty-status', data.difficulty);
            lastKnownStatus.difficulty = data.difficulty;
        }
        
        if (data.mining_reward !== lastKnownStatus.mining_reward) {
            animateNumberChange('mining-reward-status', data.mining_reward.toFixed(1));
            lastKnownStatus.mining_reward = data.mining_reward;
        }
    } catch (error) {
        showNotification('Error updating status: ' + error.message, true);
    }
}

// Animate number changes
function animateNumberChange(elementId, newValue) {
    const element = document.getElementById(elementId);
    const currentValue = parseFloat(element.textContent);
    const targetValue = parseFloat(newValue);
    
    if (currentValue === targetValue) return;
    
    // Add highlight animation
    element.classList.add('status-update');
    
    // Update the value
    element.textContent = newValue;
    
    // Remove highlight animation after it completes
    setTimeout(() => {
        element.classList.remove('status-update');
    }, 1000);
}

// Create new blockchain
async function createBlockchain() {
    const difficulty = document.getElementById('difficulty').value;
    const miningReward = document.getElementById('mining-reward').value;
    
    try {
        const response = await fetch('/api/blockchain/create', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                difficulty: parseInt(difficulty),
                mining_reward: parseFloat(miningReward)
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            showNotification(data.message);
            // Close the modal
            const modal = bootstrap.Modal.getInstance(document.getElementById('createBlockchainModal'));
            modal.hide();
            // Update the display
            updateStatus();
            updateBlockchain();
        } else {
            showNotification(data.error, true);
        }
    } catch (error) {
        showNotification('Error creating blockchain: ' + error.message, true);
    }
}

// Update blockchain display
async function updateBlockchain() {
    try {
        const response = await fetch('/api/blockchain/blocks');
        const blocks = await response.json();
        
        const container = document.getElementById('blockchain-display');
        container.innerHTML = '';
        
        blocks.forEach(block => {
            const blockElement = document.createElement('div');
            blockElement.className = 'block';
            
            blockElement.innerHTML = `
                <div class="block-header">
                    <span class="block-index">Block #${block.index}</span>
                    <span class="block-hash">${formatHash(block.hash)}</span>
                </div>
                <div class="block-details">
                    <div class="block-detail-item">
                        <span class="block-detail-label">Previous Hash</span>
                        <span class="block-detail-value">${formatHash(block.previous_hash)}</span>
                    </div>
                    <div class="block-detail-item">
                        <span class="block-detail-label">Timestamp</span>
                        <span class="block-detail-value">${formatTimestamp(block.timestamp)}</span>
                    </div>
                    <div class="block-detail-item">
                        <span class="block-detail-label">Nonce</span>
                        <span class="block-detail-value">${block.nonce}</span>
                    </div>
                </div>
                <div class="transactions-list">
                    ${block.transactions.map(tx => `
                        <div class="transaction-item">
                            <div class="transaction-details">
                                ${tx.sender} → ${tx.recipient}
                            </div>
                            <div class="transaction-amount">
                                ${tx.amount}
                            </div>
                        </div>
                    `).join('')}
                </div>
            `;
            
            container.appendChild(blockElement);
        });
        
        // Update status after blockchain update
        updateStatus();
    } catch (error) {
        showNotification('Error updating blockchain: ' + error.message, true);
    }
}

// Add transaction
document.getElementById('transaction-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const sender = document.getElementById('sender').value;
    const recipient = document.getElementById('recipient').value;
    const amount = document.getElementById('amount').value;
    
    try {
        const response = await fetch('/api/blockchain/add-transaction', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ sender, recipient, amount })
        });
        
        const data = await response.json();
        
        if (data.success) {
            showNotification('Transaction added successfully');
            e.target.reset();
            // Update status immediately after adding transaction
            updateStatus();
        } else {
            showNotification(data.error, true);
        }
    } catch (error) {
        showNotification('Error adding transaction: ' + error.message, true);
    }
});

// Mine block
document.getElementById('mining-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const minerAddress = document.getElementById('miner-address').value;
    
    // Show mining modal
    const miningModal = new bootstrap.Modal(document.getElementById('miningModal'));
    miningModal.show();
    
    // Reset mining stats
    document.getElementById('mining-attempts').textContent = '0';
    document.getElementById('mining-time').textContent = '0.0s';
    document.getElementById('mining-progress').style.width = '0%';
    
    // Start mining animation
    let attempts = 0;
    const startTime = Date.now();
    const animationInterval = setInterval(() => {
        attempts++;
        const elapsedTime = (Date.now() - startTime) / 1000;
        
        // Update stats
        document.getElementById('mining-attempts').textContent = attempts.toLocaleString();
        document.getElementById('mining-time').textContent = elapsedTime.toFixed(1) + 's';
        
        // Update progress bar (max 95% until mining is complete)
        const progress = Math.min(95, (attempts % 100) * 0.95);
        document.getElementById('mining-progress').style.width = `${progress}%`;
        
        // Update hash display with random hex
        const randomHash = Array.from({length: 10}, () => 
            Math.floor(Math.random() * 16).toString(16)).join('');
        document.querySelector('.hash-value').textContent = randomHash;
    }, 50);
    
    try {
        const response = await fetch('/api/blockchain/mine', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ miner_address: minerAddress })
        });
        
        const data = await response.json();
        
        // Stop animation
        clearInterval(animationInterval);
        
        if (data.success) {
            // Show 100% progress
            document.getElementById('mining-progress').style.width = '100%';
            // Show final hash
            document.querySelector('.hash-value').textContent = data.block.hash.substring(2, 12);
            
            // Wait a moment to show the success state
            setTimeout(() => {
                miningModal.hide();
                showNotification(`Block #${data.block.index} mined successfully in ${data.mining_duration.toFixed(2)} seconds`);
                // Update both blockchain and status after mining
                updateBlockchain();
                updateStatus();
            }, 1000);
        } else {
            miningModal.hide();
            showNotification(data.error, true);
        }
    } catch (error) {
        clearInterval(animationInterval);
        miningModal.hide();
        showNotification('Error mining block: ' + error.message, true);
    }
});

// Validate chain
async function validateChain() {
    try {
        const response = await fetch('/api/blockchain/validate');
        const data = await response.json();
        
        showNotification(data.valid ? 'Blockchain is valid' : 'Blockchain is invalid', !data.valid);
    } catch (error) {
        showNotification('Error validating chain: ' + error.message, true);
    }
}

// Save blockchain
async function saveBlockchain() {
    try {
        const response = await fetch('/api/blockchain/save');
        const data = await response.json();
        
        if (data.success) {
            showNotification('Blockchain saved successfully');
        } else {
            showNotification(data.error, true);
        }
    } catch (error) {
        showNotification('Error saving blockchain: ' + error.message, true);
    }
}

// Initial update
updateStatus();
updateBlockchain();

// Update every 5 seconds only if there are pending transactions
setInterval(() => {
    if (lastKnownStatus.pending_transactions > 0) {
        updateStatus();
        updateBlockchain();
    }
}, 5000); 