"""
Transaction Handling

Create and sign transactions using ECDSA cryptography.
"""

from dataclasses import dataclass
from typing import Optional
import hashlib
import ecdsa
import json


@dataclass
class Transaction:
    """Represents a blockchain transaction."""
    sender: str
    receiver: str
    amount: float
    signature: Optional[str] = None
    
    def to_dict(self) -> dict:
        return {
            "sender": self.sender,
            "receiver": self.receiver,
            "amount": self.amount,
            "signature": self.signature,
        }
    
    def get_hash(self) -> str:
        """Get hash of transaction data (without signature)."""
        tx_data = {
            "sender": self.sender,
            "receiver": self.receiver,
            "amount": self.amount,
        }
        tx_json = json.dumps(tx_data, sort_keys=True)
        return hashlib.sha256(tx_json.encode()).hexdigest()


class TransactionManager:
    """Manage transaction creation, signing, and verification."""
    
    def __init__(self):
        self.private_key = None
        self.public_key = None
    
    def generate_keys(self):
        """Generate ECDSA key pair."""
        self.private_key = ecdsa.SigningKey.generate(
            curve=ecdsa.NIST256p,
            hashfunc=hashlib.sha256
        )
        self.public_key = self.private_key.get_verifying_key()
    
    def get_public_key_string(self) -> str:
        """Get public key as hex string."""
        if not self.public_key:
            return ""
        return self.public_key.to_string().hex()
    
    def get_wallet_address(self) -> str:
        """
        Generate wallet address from public key.
        (Simplified: just first 8 chars of public key hash)
        """
        if not self.public_key:
            return "unknown"
        
        pub_key_bytes = self.public_key.to_string()
        pub_key_hash = hashlib.sha256(pub_key_bytes).hexdigest()
        # Format: 0x[first 8 chars]...[last 4 chars]
        return f"0x{pub_key_hash[:8]}...{pub_key_hash[-4:]}"
    
    def sign_transaction(self, transaction: Transaction) -> str:
        """
        Sign a transaction with private key.
        
        Args:
            transaction: Transaction to sign
            
        Returns:
            Signature hex string
        """
        if not self.private_key:
            raise RuntimeError("Private key not set")
        
        tx_hash = transaction.get_hash()
        tx_bytes = bytes.fromhex(tx_hash)
        
        signature = self.private_key.sign(
            tx_bytes,
            hashfunc=hashlib.sha256,
            sigencode=ecdsa.util.sigencode_string
        )
        
        return signature.hex()
    
    def create_and_sign_transaction(self, receiver: str, amount: float) -> Transaction:
        """
        Create a new transaction and sign it.
        
        Args:
            receiver: Receiver address
            amount: Transaction amount
            
        Returns:
            Signed transaction
        """
        wallet = self.get_wallet_address()
        
        tx = Transaction(
            sender=wallet,
            receiver=receiver,
            amount=amount,
        )
        
        signature = self.sign_transaction(tx)
        tx.signature = signature
        
        return tx
    
    @staticmethod
    def verify_transaction(transaction: Transaction, public_key_string: str) -> bool:
        """
        Verify a transaction signature.
        
        Args:
            transaction: Transaction with signature
            public_key_string: Public key hex string
            
        Returns:
            True if signature is valid, False otherwise
        """
        if not transaction.signature:
            return False
        
        try:
            # Reconstruct public key
            public_key = ecdsa.VerifyingKey.from_string(
                bytes.fromhex(public_key_string),
                curve=ecdsa.NIST256p,
                hashfunc=hashlib.sha256
            )
            
            tx_hash = transaction.get_hash()
            tx_bytes = bytes.fromhex(tx_hash)
            signature_bytes = bytes.fromhex(transaction.signature)
            
            # Verify signature
            public_key.verify(
                signature_bytes,
                tx_bytes,
                hashfunc=hashlib.sha256,
                sigdecode=ecdsa.util.sigdecode_string
            )
            
            return True
        except Exception:
            return False


# Test
if __name__ == "__main__":
    print("Testing Transaction and Signing\n")
    
    # Create a transaction manager
    tm = TransactionManager()
    tm.generate_keys()
    
    print(f"Wallet Address: {tm.get_wallet_address()}")
    print(f"Public Key: {tm.get_public_key_string()[:32]}...\n")
    
    # Create and sign a transaction
    tx = tm.create_and_sign_transaction("0xb7d4...e5f6", 5.0)
    
    print(f"Transaction:")
    print(f"  From: {tx.sender}")
    print(f"  To: {tx.receiver}")
    print(f"  Amount: {tx.amount}")
    print(f"  Signature: {tx.signature[:32]}...\n")
    
    # Verify signature
    is_valid = TransactionManager.verify_transaction(tx, tm.get_public_key_string())
    print(f"Signature Valid: {is_valid}")
    
    # Try to modify amount (should fail verification)
    tx.amount = 10.0
    is_valid = TransactionManager.verify_transaction(tx, tm.get_public_key_string())
    print(f"Modified tx valid: {is_valid}")
