"""
Example: Multi-Node Blockchain Simulation

Simulates 3 nodes creating transactions and mining blocks.
"""

import time
from node import Node
from miner import Miner


def main():
    """Run the blockchain simulation."""
    print("=" * 70)
    print("BLOCKCHAIN PROTOTYPE - Multi-Node Simulation")
    print("=" * 70)
    
    # Configuration
    NUM_NODES = 3
    DIFFICULTY = 3  # Lower difficulty for faster demo
    INITIAL_BALANCE = 100.0
    
    # Create nodes
    print(f"\n=== Node Startup ({NUM_NODES} nodes) ===")
    nodes = [Node(i+1, 5000+i+1, difficulty=DIFFICULTY) for i in range(NUM_NODES)]
    
    for node in nodes:
        node.wallet.balance = INITIAL_BALANCE
        node.print_status()
    
    # Connect nodes as peers
    print("\n[INFO] Connecting peers...")
    for i, node in enumerate(nodes):
        for j, peer in enumerate(nodes):
            if i != j:
                node.add_peer(peer)
    
    # Start miners
    print("\n[INFO] Starting miners...")
    miners = [Miner(node, mining_interval=0.5) for node in nodes]
    for miner in miners:
        miner.start()
    
    print()
    
    # Simulate transactions
    print("=== Creating Transactions ===")
    
    time.sleep(1)
    
    # Transaction 1: Node 1 sends to Node 2
    print(f"\n[NODE-1] Creating transaction:")
    print(f"         From:   {nodes[0].wallet.address}")
    print(f"         To:     {nodes[1].wallet.address}")
    print(f"         Amount: 2.5 coins")
    nodes[0].create_transaction(nodes[1].wallet.address, 2.5)
    
    time.sleep(2)
    
    # Transaction 2: Node 2 sends to Node 3
    print(f"\n[NODE-2] Creating transaction:")
    print(f"         From:   {nodes[1].wallet.address}")
    print(f"         To:     {nodes[2].wallet.address}")
    print(f"         Amount: 1.5 coins")
    nodes[1].create_transaction(nodes[2].wallet.address, 1.5)
    
    time.sleep(3)
    
    # Stop mining
    print("\n[INFO] Stopping miners...")
    for miner in miners:
        miner.stop()
    
    # Print final state
    print("\n" + "=" * 70)
    print("=== Final State ===")
    print("=" * 70)
    
    # Verify chain consistency
    print("\n[INFO] Verifying chains...")
    for node in nodes:
        is_valid = node.blockchain.is_chain_valid()
        print(f"[NODE-{node.node_id}] Chain valid: {is_valid}")
    
    # Print balances
    print("\n=== Wallet Balances ===")
    
    for i, node in enumerate(nodes):
        address = node.wallet.address
        balance = node.get_balance()
        print(f"{address}  {balance:6.1f} coins")
    
    # Show transaction history
    print("\n=== Transaction History ===")
    
    for i, node in enumerate(nodes):
        print(f"\n[NODE-{node.node_id}] Blockchain:")
        node.print_chain()
    
    print("\n" + "=" * 70)
    print(f"Simulation complete!")
    print(f"Total blocks: {nodes[0].blockchain.get_chain_length()}")
    print("=" * 70)


if __name__ == "__main__":
    main()
