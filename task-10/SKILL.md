# Skill: Task 10 - Blockchain Prototype

This skill provides comprehensive guidance for understanding and extending the blockchain implementation.

## Overview

Task 10 implements a simplified blockchain with proof-of-work mining, ECDSA digital signatures, wallet management, and P2P peer discovery. Multiple nodes can connect, exchange blocks, and maintain a distributed ledger.

## Project Architecture

### Components

1. **blockchain.py**: Core blockchain data structure, block validation, chain integrity
2. **transaction.py**: Transaction creation, ECDSA signing, verification
3. **wallet.py**: Key generation (ECDSA), balance tracking (UTXO-based)
4. **node.py**: P2P node with peer discovery and gossip protocol
5. **miner.py**: Mining logic, proof-of-work calculation, nonce search
6. **example.py**: Multi-node simulation with transactions and mining

## Blockchain Concepts

### Proof-of-Work

Mining tries nonces until hash starts with N zeros (difficulty target):

```
Block hash: 000abc123def...  (3 leading zeros)
Difficulty: 3
```

Higher difficulty = more computation required = longer to mine.

### Digital Signatures (ECDSA)

Each transaction is signed with sender's private key:

1. Sender signs: `signature = sign(transaction_data, private_key)`
2. Network verifies: `verify(signature, transaction_data, public_key)`
3. Ensures non-repudiation: only holder of private key could sign

### UTXO Model (Unspent Transaction Output)

Balance tracking is based on unspent outputs:

- Each transaction output can only be spent once
- Wallet maintains list of spendable outputs
- Balance = sum of all unspent outputs for wallet address

### Merkle Tree

Transaction integrity verification:

- All transactions hashed together into root hash
- Root hash stored in block header
- Any transaction change invalidates root hash

## Running the Blockchain

### Single Node Simulation

```bash
cd task-10
python example.py
```

Demonstrates:

- 3 nodes starting up with unique wallets
- Peer discovery and connection
- Mining process with nonce-finding
- Transaction creation and signing
- Block propagation across network
- Final blockchain state on all nodes

### Output Interpretation

```
[NODE-1] Mining started        # Node 1 starts mining blocks
[NODE-2] Block #1 mined        # Node 2 finds valid block #1
Hash: 0005b08a2a6c7378...      # Block hash with leading zeros (difficulty met)
Nonce: 517                      # Number of iterations to find valid hash
```

## Common Tasks & Solutions

### Understanding Wallet Operations

**View balance**:

```python
balance = wallet.get_balance()  # Sum of unspent outputs
```

**Create transaction**:

```python
tx = wallet.create_transaction(
    recipient="0xabc123...",
    amount=5.0
)
# Returns signed transaction
```

### Debugging Mining Issues

**Problem**: Mining takes very long

- Check difficulty setting (higher = slower)
- Verify hash function is correctly computing leading zeros
- Check nonce iteration isn't stuck in loop

**Problem**: Blocks not propagating to peers

- Verify node connections are established
- Check gossip protocol broadcasts to all peers
- Verify block validation logic isn't rejecting valid blocks

### Simulating Different Scenarios

**Faster mining** (reduce difficulty):

- Edit `blockchain.py` difficulty constant from 4 to 2
- Blocks mine faster but require less computation

**More nodes** (increase network):

- Edit `example.py` to create more node instances
- Demonstrates P2P scalability

**Fork detection**:

- Add transaction that creates fork in chain
- Observe how nodes handle conflicting blocks
- Verify chain selection (longest chain wins)

## Key Files to Understand

- `blockchain.py` lines 1-50: Block class and hashing
- `blockchain.py` lines 51-100: Chain class and validation
- `transaction.py`: ECDSA signing and verification
- `wallet.py`: Key generation and balance tracking
- `miner.py`: Proof-of-work implementation
- `node.py`: P2P discovery and gossip protocol

## Performance Tuning

### Block Size

- Fewer transactions = faster mining
- More transactions = longer validation

### Difficulty

- Lower difficulty = faster blocks but less security
- Higher difficulty = slower blocks but more secure

### Network Latency

- Smaller block propagation delay = faster consensus
- Simulate latency with `time.sleep()` in gossip protocol

## Testing Locally

Key things to verify:

1. All nodes have valid chains (verify returns True)
2. Block hashes have required leading zeros
3. Transactions are properly signed and verified
4. Balances are consistent across nodes (after convergence)
5. No double-spending occurs (UTXO consumed only once)
