# Task 10: Blockchain Prototype

A simplified blockchain implementation with proof-of-work consensus, transaction signing, peer-to-peer block propagation, and a wallet system. Multiple nodes can discover each other and maintain a distributed ledger.

## Features

- **Blockchain Core**: Chain data structure with block hashing and validation
- **Proof-of-Work**: Adjustable difficulty with nonce-based mining
- **Digital Signatures**: ECDSA transaction signing for non-repudiation
- **Wallet System**: Create wallets, manage keys, query balances
- **Peer Discovery**: Nodes advertise and connect to peers on a network
- **Block Propagation**: Gossip protocol for distributed consensus
- **Merkle Tree**: Transaction integrity verification
- **Multi-Node Simulation**: Run multiple nodes in parallel
- **Balance Tracking**: UTXO-based wallet balance management

## Project Structure

```
task-10/
├── README.md
├── requirements.txt
├── blockchain.py         # Core blockchain and block classes
├── transaction.py        # Transaction creation and signing
├── wallet.py             # Wallet management and key handling
├── node.py               # P2P node with gossip protocol
├── miner.py              # Mining and block creation
└── example.py            # Multi-node simulation
```

## How It Works

### 1. Wallet Creation

Each node has a private/public key pair generated using ECDSA cryptography.
Wallets sign transactions to prove ownership.

### 2. Transaction Lifecycle

- User creates a transaction specifying sender, receiver, and amount
- Transaction is digitally signed with sender's private key
- Signature is verified by the network using sender's public key
- Transactions placed in mempool awaiting mining

### 3. Mining Process

- Miners collect transactions from mempool
- Create a new block with all pending transactions
- Find a nonce that satisfies the difficulty target (hash starts with N zeros)
- Broadcast mined block to all peers
- Peers validate and append the block

### 4. Consensus

Each node independently validates incoming blocks:

- Verify all signatures
- Check no double-spending
- Verify proof-of-work
- Append to local chain

### 5. Balances

Balances computed by scanning the chain for all transactions:

- Incoming transactions increase balance
- Outgoing transactions decrease balance
- Mining rewards credited to miner

## Running the Application

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Run the simulation

```bash
python example.py
```

Expected output:

```
=== Node Startup (3 nodes) ===
[NODE-1] Listening on port 5001 | Wallet: 0xa3f8...c1d2
[NODE-2] Listening on port 5002 | Wallet: 0xb7d4...e5f6
[NODE-3] Listening on port 5003 | Wallet: 0xc9e2...a7b8

=== Transaction ===
[NODE-1] Creating transaction:
         From:   0xa3f8...c1d2
         To:     0xb7d4...e5f6
         Amount: 2.5 coins
         Signature: 3045022100...  Valid

=== Mining ===
[NODE-2] Mining block #7 (2 transactions in mempool)...
         Difficulty: 4 (hash must start with "0000")
         Nonce: 0      -> hash: 8a3f1b...     MISS
         Nonce: 1      -> hash: c72de9...     MISS
         ...
         Nonce: 48,231 -> hash: 0000a8f3c1... FOUND!

=== Propagation ===
[NODE-2] Broadcasting block #7 to peers...
[NODE-1] Received block #7 — validating... Accepted (chain height: 7)
[NODE-3] Received block #7 — validating... Accepted (chain height: 7)

=== Wallet Balances ===
0xa3f8...c1d2:  7.5 coins
0xb7d4...e5f6: 13.5 coins (includes mining rewards)
0xc9e2...a7b8:  4.0 coins
```

## Architecture Patterns

- **Proof-of-Work**: Hashcash-style difficulty adjustment
- **Digital Signatures**: ECDSA for transaction non-repudiation
- **Merkle Tree**: Hash-based transaction integrity
- **Gossip Protocol**: Peer-to-peer block propagation
- **UTXO Model**: Unspent transaction output balance tracking
- **Consensus**: Longest chain rule

## Security Considerations

- **Transaction Validation**: Verify signatures on all transactions
- **Double-Spending**: Track spent outputs to prevent reuse
- **51% Attack**: Minority of nodes cannot outpace majority
- **Sybil Resistance**: Proof-of-work makes large-scale attacks expensive

## Customization

- **Difficulty**: Change `DIFFICULTY` in `example.py` (higher = harder)
- **Mining Reward**: Adjust `MINING_REWARD` in `miner.py`
- **Node Count**: Modify `NUM_NODES` in `example.py`
- **Initial Balances**: Edit `initial_balance` distribution in `example.py`

## Learning Outcomes

- ✅ Blockchain data structures and hashing
- ✅ Proof-of-work consensus algorithm
- ✅ Public-key cryptography (ECDSA)
- ✅ Merkle tree construction
- ✅ Peer-to-peer gossip protocols
- ✅ Distributed consensus and fork resolution
- ✅ UTXO-based wallet balancing
- ✅ Thread-safe concurrent mining
