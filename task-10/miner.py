"""
Mining Pool and Worker

Simplified mining implementation.
"""

import threading
import time
from typing import Optional, Callable


class Miner:
    """
    Mining worker that repeatedly attempts to mine blocks.
    """
    
    def __init__(self, node, mining_interval: float = 5.0):
        """
        Args:
            node: Node instance to mine for
            mining_interval: Time between mining attempts (seconds)
        """
        self.node = node
        self.mining_interval = mining_interval
        self.is_running = False
        self.thread = None
        self.block_callback: Optional[Callable] = None
    
    def start(self):
        """Start the mining thread."""
        if self.is_running:
            return
        
        self.is_running = True
        self.thread = threading.Thread(target=self._mining_loop, daemon=True)
        self.thread.start()
        print(f"[NODE-{self.node.node_id}] Mining started")
    
    def stop(self):
        """Stop the mining thread."""
        self.is_running = False
        if self.thread:
            self.thread.join(timeout=5)
        print(f"[NODE-{self.node.node_id}] Mining stopped")
    
    def _mining_loop(self):
        """Main mining loop."""
        while self.is_running:
            # Try to mine a block
            if len(self.node.blockchain.pending_transactions) > 0:
                block_info = self.node.mine()
                
                if block_info:
                    print(f"[NODE-{self.node.node_id}] Block #{block_info['index']} mined! "
                          f"Hash: {block_info['hash'][:16]}... "
                          f"Nonce: {block_info['nonce']}")
                    
                    if self.block_callback:
                        self.block_callback(block_info)
            
            # Wait before next mining attempt
            time.sleep(self.mining_interval)
    
    def set_block_callback(self, callback: Callable):
        """Set a callback function when a block is mined."""
        self.block_callback = callback


if __name__ == "__main__":
    from node import Node
    
    print("Testing Miner\n")
    
    node = Node(1, 5001, difficulty=2)
    miner = Miner(node, mining_interval=1.0)
    
    # Add test transaction
    node.wallet.balance = 100.0
    node.create_transaction("0xtest...1234", 10.0)
    
    print("Starting miner...\n")
    miner.start()
    
    # Let it mine for 5 seconds
    time.sleep(5)
    
    miner.stop()
    
    print(f"\nBlocks mined: {node.blockchain.get_chain_length() - 1}")
