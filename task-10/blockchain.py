"""
Core Blockchain Implementation

Provides Block and Blockchain classes with proof-of-work validation.
"""

import hashlib
import json
from typing import List, Optional, Dict
from dataclasses import dataclass, asdict, field
from datetime import datetime


@dataclass
class Block:
    """Represents a block in the blockchain."""
    index: int
    timestamp: str
    transactions: List[Dict]
    previous_hash: str
    nonce: int = 0
    hash: str = ""
    
    def compute_hash(self) -> str:
        """Compute the SHA-256 hash of this block."""
        block_data = {
            "index": self.index,
            "timestamp": self.timestamp,
            "transactions": self.transactions,
            "previous_hash": self.previous_hash,
            "nonce": self.nonce,
        }
        block_json = json.dumps(block_data, sort_keys=True)
        return hashlib.sha256(block_json.encode()).hexdigest()
    
    def __str__(self):
        return (f"Block #{self.index}\n"
                f"  Hash: {self.hash[:16]}...\n"
                f"  Prev: {self.previous_hash[:16]}...\n"
                f"  Txns: {len(self.transactions)}\n"
                f"  Nonce: {self.nonce}")


class Blockchain:
    """
    Blockchain management with proof-of-work validation.
    """
    
    GENESIS_PREVIOUS_HASH = "0"
    
    def __init__(self, difficulty: int = 2):
        """
        Initialize blockchain.
        
        Args:
            difficulty: Number of leading zeros required in hash
        """
        self.chain: List[Block] = []
        self.pending_transactions: List[Dict] = []
        self.difficulty = difficulty
        
        # Create genesis block
        self._create_genesis_block()
    
    def _create_genesis_block(self):
        """Create the first block in the chain."""
        genesis_block = Block(
            index=0,
            timestamp=datetime.now().isoformat(),
            transactions=[],
            previous_hash=self.GENESIS_PREVIOUS_HASH,
        )
        genesis_block.hash = genesis_block.compute_hash()
        self.chain.append(genesis_block)
    
    def get_last_block(self) -> Block:
        """Get the most recent block."""
        return self.chain[-1]
    
    def add_transaction(self, transaction: Dict) -> bool:
        """
        Add a transaction to the pending pool.
        
        Args:
            transaction: Transaction dict with from, to, amount, signature
            
        Returns:
            True if valid, False otherwise
        """
        # Validate transaction (in real chain, verify signature here)
        if not self._validate_transaction(transaction):
            return False
        
        self.pending_transactions.append(transaction)
        return True
    
    def _validate_transaction(self, transaction: Dict) -> bool:
        """Validate a transaction."""
        required_fields = ["sender", "receiver", "amount", "signature"]
        return all(field in transaction for field in required_fields)
    
    def mine_block(self, miner_wallet: str) -> Block:
        """
        Mine a new block with pending transactions.
        
        Args:
            miner_wallet: Wallet address of the miner
            
        Returns:
            Newly mined block
        """
        last_block = self.get_last_block()
        
        # Include pending transactions plus mining reward
        transactions = self.pending_transactions.copy()
        transactions.append({
            "sender": "SYSTEM",
            "receiver": miner_wallet,
            "amount": 1.0,  # Mining reward
            "signature": "mining-reward",
        })
        
        new_block = Block(
            index=len(self.chain),
            timestamp=datetime.now().isoformat(),
            transactions=transactions,
            previous_hash=last_block.hash,
        )
        
        # Perform proof-of-work
        nonce = 0
        while True:
            new_block.nonce = nonce
            new_block.hash = new_block.compute_hash()
            
            if new_block.hash.startswith("0" * self.difficulty):
                break
            
            nonce += 1
        
        # Clear pending transactions
        self.pending_transactions.clear()
        
        # Add to chain
        self.chain.append(new_block)
        
        return new_block
    
    def is_chain_valid(self) -> bool:
        """
        Verify the entire blockchain.
        
        Returns:
            True if valid, False if corrupted
        """
        for i in range(1, len(self.chain)):
            current = self.chain[i]
            previous = self.chain[i - 1]
            
            # Verify hash
            if current.hash != current.compute_hash():
                print(f"Invalid hash at block {i}")
                return False
            
            # Verify previous hash link
            if current.previous_hash != previous.hash:
                print(f"Invalid previous hash link at block {i}")
                return False
            
            # Verify proof-of-work
            if not current.hash.startswith("0" * self.difficulty):
                print(f"Invalid proof-of-work at block {i}")
                return False
        
        return True
    
    def get_balance(self, wallet: str) -> float:
        """
        Calculate wallet balance from chain history.
        
        Args:
            wallet: Wallet address
            
        Returns:
            Current balance
        """
        balance = 0.0
        
        # Scan all blocks
        for block in self.chain:
            for tx in block.transactions:
                if tx["receiver"] == wallet:
                    balance += tx["amount"]
                if tx["sender"] == wallet:
                    balance -= tx["amount"]
        
        return balance
    
    def get_chain_length(self) -> int:
        """Get the number of blocks in the chain."""
        return len(self.chain)
    
    def print_chain(self):
        """Print the entire blockchain."""
        print(f"\nBlockchain ({len(self.chain)} blocks):")
        for block in self.chain:
            print(f"\n{block}")


# Test
if __name__ == "__main__":
    blockchain = Blockchain(difficulty=2)
    
    print("Testing blockchain with difficulty=2\n")
    
    # Add transactions
    blockchain.add_transaction({
        "sender": "alice",
        "receiver": "bob",
        "amount": 10.0,
        "signature": "sig1",
    })
    
    # Mine a block
    print("Mining block...")
    block = blockchain.mine_block("miner1")
    print(f"Block mined: {block.hash}\n")
    
    # Add more transactions
    blockchain.add_transaction({
        "sender": "bob",
        "receiver": "charlie",
        "amount": 5.0,
        "signature": "sig2",
    })
    
    # Mine another block
    print("Mining another block...")
    block = blockchain.mine_block("miner1")
    print(f"Block mined: {block.hash}\n")
    
    # Check balances
    print("Balances:")
    print(f"  alice:   {blockchain.get_balance('alice')}")
    print(f"  bob:     {blockchain.get_balance('bob')}")
    print(f"  charlie: {blockchain.get_balance('charlie')}")
    print(f"  miner1:  {blockchain.get_balance('miner1')}")
    
    # Verify chain
    print(f"\nChain valid: {blockchain.is_chain_valid()}")
    
    blockchain.print_chain()
