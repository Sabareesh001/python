"""
Response caching with TTL support.
"""

import time
from typing import Optional, Any, Dict
import threading
from hashlib import md5


class CacheEntry:
    """Represents a cached response."""
    
    def __init__(self, content: Any, ttl: int = 300):
        self.content = content
        self.ttl = ttl
        self.created_at = time.time()
        self.hits = 0
    
    def is_expired(self) -> bool:
        """Check if cache entry has expired."""
        return (time.time() - self.created_at) > self.ttl
    
    def get_ttl_remaining(self) -> int:
        """Get remaining TTL in seconds."""
        elapsed = time.time() - self.created_at
        return max(0, self.ttl - int(elapsed))


class ResponseCache:
    """Cache for API responses with TTL."""
    
    def __init__(self):
        self._cache: Dict[str, CacheEntry] = {}
        self._lock = threading.RLock()
        self.hits = 0
        self.misses = 0
    
    def _generate_key(self, method: str, path: str, params: Dict[str, Any] = None) -> str:
        """Generate cache key from request."""
        key_str = f"{method}:{path}"
        if params:
            params_str = "&".join(f"{k}={v}" for k, v in sorted(params.items()))
            key_str += f"?{params_str}"
        
        # Use MD5 for shorter keys
        return md5(key_str.encode()).hexdigest()
    
    def get(self, method: str, path: str, params: Dict[str, Any] = None) -> Optional[Any]:
        """Get cached response."""
        key = self._generate_key(method, path, params)
        
        with self._lock:
            if key not in self._cache:
                self.misses += 1
                return None
            
            entry = self._cache[key]
            
            # Check expiration
            if entry.is_expired():
                del self._cache[key]
                self.misses += 1
                return None
            
            entry.hits += 1
            self.hits += 1
            return entry.content
    
    def set(self, method: str, path: str, content: Any, ttl: int = 300, params: Dict[str, Any] = None) -> None:
        """Cache a response."""
        key = self._generate_key(method, path, params)
        
        with self._lock:
            self._cache[key] = CacheEntry(content, ttl)
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        with self._lock:
            total = self.hits + self.misses
            hit_rate = (self.hits / total * 100) if total > 0 else 0
            
            return {
                'total_entries': len(self._cache),
                'total_hits': self.hits,
                'total_misses': self.misses,
                'hit_rate': f"{hit_rate:.1f}%",
            }
    
    def clear(self) -> None:
        """Clear all cache entries."""
        with self._lock:
            self._cache.clear()
    
    def cleanup_expired(self) -> int:
        """Remove expired entries. Returns count removed."""
        with self._lock:
            expired_keys = [
                key for key, entry in self._cache.items()
                if entry.is_expired()
            ]
            
            for key in expired_keys:
                del self._cache[key]
            
            return len(expired_keys)
