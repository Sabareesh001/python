"""
Wallet Management

Create and manage blockchain wallets with key storage.
"""

from transaction import TransactionManager, Transaction
from typing import Optional


class Wallet:
    """
    Represents a blockchain wallet with a key pair and balance.
    """
    
    def __init__(self, name: str = "default"):
        self.name = name
        self.tx_manager = TransactionManager()
        self.tx_manager.generate_keys()
        self.address = self.tx_manager.get_wallet_address()
        self.balance = 0.0
    
    def get_public_key(self) -> str:
        """Get the wallet's public key."""
        return self.tx_manager.get_public_key_string()
    
    def create_transaction(self, receiver: str, amount: float) -> Optional[Transaction]:
        """
        Create and sign a transaction from this wallet.
        
        Args:
            receiver: Recipient address
            amount: Amount to send
            
        Returns:
            Signed transaction if sufficient balance, None otherwise
        """
        if amount > self.balance:
            print(f"[ERROR] Insufficient balance: {self.balance} < {amount}")
            return None
        
        # Create and sign transaction
        tx = self.tx_manager.create_and_sign_transaction(receiver, amount)
        
        return tx
    
    def receive(self, amount: float):
        """Receive coins."""
        self.balance += amount
    
    def send(self, amount: float):
        """Deduct coins (called after transaction is confirmed)."""
        self.balance -= amount
    
    def __str__(self):
        return f"Wallet({self.name}: {self.address}, balance={self.balance})"


class WalletManager:
    """Manages multiple wallets."""
    
    def __init__(self):
        self.wallets: dict[str, Wallet] = {}
    
    def create_wallet(self, name: str, initial_balance: float = 0.0) -> Wallet:
        """Create a new wallet."""
        wallet = Wallet(name)
        wallet.balance = initial_balance
        self.wallets[wallet.address] = wallet
        return wallet
    
    def get_wallet(self, address: str) -> Optional[Wallet]:
        """Get wallet by address."""
        return self.wallets.get(address)
    
    def list_wallets(self):
        """List all wallets."""
        print("\nWallets:")
        for address, wallet in self.wallets.items():
            print(f"  {wallet.name:15} {address:20} balance={wallet.balance:.2f}")


# Test
if __name__ == "__main__":
    print("Testing Wallet Management\n")
    
    manager = WalletManager()
    
    # Create wallets
    alice = manager.create_wallet("alice", initial_balance=100.0)
    bob = manager.create_wallet("bob", initial_balance=50.0)
    charlie = manager.create_wallet("charlie", initial_balance=25.0)
    
    manager.list_wallets()
    
    # Create a transaction
    print(f"\nAlice sends 10 coins to Bob...")
    tx = alice.create_transaction(bob.address, 10.0)
    
    if tx:
        print(f"Transaction created:")
        print(f"  From: {tx.sender}")
        print(f"  To: {tx.receiver}")
        print(f"  Amount: {tx.amount}")
        print(f"  Signature: {tx.signature[:16]}...")
