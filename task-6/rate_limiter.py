"""
Rate limiting implementation using token bucket algorithm.
"""

import time
from typing import Dict
from collections import defaultdict
import threading


class TokenBucket:
    """Token bucket rate limiter."""
    
    def __init__(self, capacity: float, refill_rate: float):
        """
        Args:
            capacity: Maximum tokens (requests per window)
            refill_rate: Tokens added per second
        """
        self.capacity = capacity
        self.refill_rate = refill_rate
        self.tokens = capacity
        self.last_refill = time.time()
        self._lock = threading.Lock()
    
    def try_consume(self, tokens: int = 1) -> bool:
        """Try to consume tokens. Returns True if allowed."""
        with self._lock:
            self._refill()
            
            if self.tokens >= tokens:
                self.tokens -= tokens
                return True
            
            return False
    
    def _refill(self) -> None:
        """Refill tokens based on elapsed time."""
        now = time.time()
        elapsed = now - self.last_refill
        tokens_to_add = elapsed * self.refill_rate
        
        self.tokens = min(self.capacity, self.tokens + tokens_to_add)
        self.last_refill = now
    
    def get_remaining(self) -> float:
        """Get remaining tokens."""
        with self._lock:
            self._refill()
            return self.tokens


class RateLimiter:
    """Rate limiter for API keys/clients."""
    
    def __init__(self, requests_per_minute: int = 60):
        self.requests_per_minute = requests_per_minute
        self.refill_rate = requests_per_minute / 60.0  # tokens per second
        self.buckets: Dict[str, TokenBucket] = defaultdict(
            lambda: TokenBucket(requests_per_minute, self.refill_rate)
        )
    
    def is_allowed(self, client_id: str) -> bool:
        """Check if request is allowed for client."""
        bucket = self.buckets[client_id]
        return bucket.try_consume(1)
    
    def get_remaining_requests(self, client_id: str) -> int:
        """Get remaining requests for client."""
        bucket = self.buckets[client_id]
        return int(bucket.get_remaining())
    
    def get_client_stats(self, client_id: str) -> Dict[str, any]:
        """Get rate limit stats for client."""
        bucket = self.buckets[client_id]
        remaining = bucket.get_remaining()
        
        return {
            'client_id': client_id,
            'limit': self.requests_per_minute,
            'remaining': int(remaining),
            'reset_in_seconds': (self.requests_per_minute - remaining) / self.refill_rate if remaining < self.requests_per_minute else 0,
        }
