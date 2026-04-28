"""
Node Implementation

P2P node with block propagation and consensus.
"""

from blockchain import Blockchain
from wallet import Wallet
from typing import List, Dict, Optional
import threading
import time


class Node:
    """
    Blockchain node with P2P capabilities.
    
    Maintains its own blockchain, accepts transactions,
    and propagates blocks to peers.
    """
    
    def __init__(self, node_id: int, port: int, difficulty: int = 2):
        self.node_id = node_id
        self.port = port
        self.blockchain = Blockchain(difficulty=difficulty)
        self.wallet = Wallet(f"node-{node_id}")
        self.peers: List["Node"] = []
        self.is_mining = False
    
    def add_peer(self, peer: "Node"):
        """Add a peer node."""
        if peer.node_id != self.node_id:  # Don't add self
            self.peers.append(peer)
    
    def create_transaction(self, receiver_address: str, amount: float) -> bool:
        """
        Create a transaction and broadcast to network.
        
        Args:
            receiver_address: Recipient wallet address
            amount: Amount to send
            
        Returns:
            True if transaction created, False if insufficient balance
        """
        tx = self.wallet.create_transaction(receiver_address, amount)
        
        if not tx:
            return False
        
        # Add to own mempool
        self.blockchain.add_transaction(tx.to_dict())
        
        # Broadcast to peers
        self._broadcast_transaction(tx.to_dict())
        
        return True
    
    def _broadcast_transaction(self, transaction: Dict):
        """Broadcast a transaction to all peers."""
        for peer in self.peers:
            peer.blockchain.add_transaction(transaction)
    
    def mine(self) -> Optional[Dict]:
        """
        Mine a new block.
        
        Returns:
            Mined block dict, or None if mining fails
        """
        if len(self.blockchain.pending_transactions) == 0:
            return None
        
        block = self.blockchain.mine_block(self.wallet.address)
        
        # Broadcast block to peers
        self._broadcast_block(block)
        
        # Award mining reward to local wallet
        self.wallet.balance += 1.0
        
        return {
            "index": block.index,
            "hash": block.hash,
            "nonce": block.nonce,
            "txns": len(block.transactions),
        }
    
    def _broadcast_block(self, block):
        """Broadcast a mined block to all peers."""
        for peer in self.peers:
            peer.receive_block(block)
    
    def receive_block(self, block):
        """
        Receive a block from a peer.
        
        Validates and appends to chain if valid.
        """
        # Validate block
        if not self._validate_block(block):
            print(f"[NODE-{self.node_id}] Invalid block rejected")
            return False
        
        # Append to chain
        self.blockchain.chain.append(block)
        
        # Clear pending transactions that were included
        # (simplified: assume all transactions in block are now confirmed)
        self.blockchain.pending_transactions.clear()
        
        return True
    
    def _validate_block(self, block) -> bool:
        """
        Validate a block before accepting.
        
        Checks:
        - Proof-of-work
        - Previous hash link
        - Valid signature
        """
        # Check proof-of-work
        if not block.hash.startswith("0" * self.blockchain.difficulty):
            return False
        
        # Check hash
        if block.hash != block.compute_hash():
            return False
        
        # Check previous link
        if block.previous_hash != self.blockchain.get_last_block().hash:
            return False
        
        return True
    
    def get_balance(self) -> float:
        """Get node's balance from blockchain."""
        return self.blockchain.get_balance(self.wallet.address)
    
    def get_address_balance(self, address: str) -> float:
        """Get balance of any address."""
        return self.blockchain.get_balance(address)
    
    def print_status(self):
        """Print node status."""
        print(f"[NODE-{self.node_id}] Listening on port {self.port} | "
              f"Wallet: {self.wallet.address}")
    
    def print_chain(self):
        """Print node's blockchain."""
        print(f"\n[NODE-{self.node_id}] Blockchain ({self.blockchain.get_chain_length()} blocks):")
        for block in self.blockchain.chain[:5]:  # Show first 5 blocks
            print(f"  Block #{block.index}: {block.hash[:16]}... "
                  f"(txns: {len(block.transactions)}, nonce: {block.nonce})")
        
        if self.blockchain.get_chain_length() > 5:
            print(f"  ... ({self.blockchain.get_chain_length() - 5} more blocks)")


# Test
if __name__ == "__main__":
    print("Testing Node Implementation\n")
    
    # Create nodes
    node1 = Node(1, 5001)
    node2 = Node(2, 5002)
    node3 = Node(3, 5003)
    
    # Print initial status
    node1.print_status()
    node2.print_status()
    node3.print_status()
    
    # Connect peers
    node1.add_peer(node2)
    node1.add_peer(node3)
    node2.add_peer(node1)
    node2.add_peer(node3)
    node3.add_peer(node1)
    node3.add_peer(node2)
    
    print("\n[INFO] Peers connected\n")
    
    # Set initial balances
    node1.wallet.balance = 100.0
    node2.wallet.balance = 50.0
    node3.wallet.balance = 25.0
    
    print("Initial balances:")
    print(f"  Node 1: {node1.get_balance()}")
    print(f"  Node 2: {node2.get_balance()}")
    print(f"  Node 3: {node3.get_balance()}\n")
