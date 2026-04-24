"""
Circuit breaker pattern for fault tolerance.
Prevents cascading failures by opening circuit after threshold failures.
"""

import time
from typing import Optional, Dict, Callable, Any
from enum import Enum
import threading


class CircuitState(Enum):
    """Circuit breaker states."""
    CLOSED = "CLOSED"          # Normal operation
    OPEN = "OPEN"              # Failing, reject requests
    HALF_OPEN = "HALF_OPEN"   # Testing if service recovered


class CircuitBreaker:
    """Circuit breaker for a single service/endpoint."""
    
    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: int = 30,
        success_threshold: int = 2
    ):
        """
        Args:
            failure_threshold: Failures before opening circuit
            recovery_timeout: Seconds before attempting recovery
            success_threshold: Successes in HALF_OPEN before closing
        """
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.success_threshold = success_threshold
        
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time = None
        self.opened_at = None
        
        self._lock = threading.RLock()
    
    def call(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function through circuit breaker."""
        with self._lock:
            self._check_state()
            
            if self.state == CircuitState.OPEN:
                raise CircuitBreakerOpenError(
                    f"Circuit breaker is OPEN. Retry in {self.recovery_timeout}s"
                )
        
        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise
    
    def _check_state(self) -> None:
        """Check and potentially transition state."""
        if self.state == CircuitState.OPEN:
            # Check if recovery timeout has passed
            if self.opened_at and (time.time() - self.opened_at) > self.recovery_timeout:
                self.state = CircuitState.HALF_OPEN
                self.success_count = 0
                self.failure_count = 0
    
    def _on_success(self) -> None:
        """Handle successful call."""
        self.failure_count = 0
        
        if self.state == CircuitState.HALF_OPEN:
            self.success_count += 1
            if self.success_count >= self.success_threshold:
                self.state = CircuitState.CLOSED
                self.success_count = 0
    
    def _on_failure(self) -> None:
        """Handle failed call."""
        self.last_failure_time = time.time()
        self.failure_count += 1
        
        if self.state == CircuitState.HALF_OPEN:
            # Failure while testing recovery
            self.state = CircuitState.OPEN
            self.opened_at = time.time()
        elif self.failure_count >= self.failure_threshold:
            # Open circuit after threshold failures
            self.state = CircuitState.OPEN
            self.opened_at = time.time()
    
    def get_status(self) -> Dict[str, Any]:
        """Get circuit breaker status."""
        with self._lock:
            return {
                'state': self.state.value,
                'failure_count': self.failure_count,
                'success_count': self.success_count,
                'last_failure': self.last_failure_time,
                'opened_at': self.opened_at,
            }


class CircuitBreakerManager:
    """Manages circuit breakers for multiple services."""
    
    def __init__(self):
        self.breakers: Dict[str, CircuitBreaker] = {}
    
    def get_breaker(self, service_name: str) -> CircuitBreaker:
        """Get or create circuit breaker for service."""
        if service_name not in self.breakers:
            self.breakers[service_name] = CircuitBreaker()
        
        return self.breakers[service_name]
    
    def call(self, service_name: str, func: Callable, *args, **kwargs) -> Any:
        """Call function through circuit breaker."""
        breaker = self.get_breaker(service_name)
        return breaker.call(func, *args, **kwargs)
    
    def get_all_status(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all circuit breakers."""
        return {name: breaker.get_status() for name, breaker in self.breakers.items()}


class CircuitBreakerOpenError(Exception):
    """Raised when circuit breaker is open."""
    pass
