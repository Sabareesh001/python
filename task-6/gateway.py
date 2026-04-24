"""
Async API Gateway with rate limiting, caching, and circuit breaker.
Routes requests to downstream microservices.
"""

import asyncio
import aiohttp
import time
from typing import Dict, Optional, Any, Callable
from dataclasses import dataclass
from rate_limiter import RateLimiter
from cache import ResponseCache
from circuit_breaker import CircuitBreakerManager, CircuitBreakerOpenError
import json


@dataclass
class Route:
    """API route configuration."""
    path_prefix: str
    upstream_url: str
    cache_ttl: int = 300


class APIGateway:
    """Reverse proxy API gateway with advanced features."""
    
    def __init__(self, host: str = "0.0.0.0", port: int = 8080):
        self.host = host
        self.port = port
        
        self.routes: Dict[str, Route] = {}
        self.rate_limiter = RateLimiter(requests_per_minute=50)
        self.cache = ResponseCache()
        self.circuit_breaker_manager = CircuitBreakerManager()
        
        # Request tracking
        self.total_requests = 0
        self.rate_limited_requests = 0
        self.cache_hits = 0
        self.circuit_broken_requests = 0
    
    def add_route(self, path_prefix: str, upstream_url: str, cache_ttl: int = 300) -> None:
        """Register a route."""
        self.routes[path_prefix] = Route(path_prefix, upstream_url, cache_ttl)
        print(f"[GATEWAY] Route registered: {path_prefix} -> {upstream_url}")
    
    async def handle_request(
        self,
        method: str,
        path: str,
        api_key: str,
        body: Optional[str] = None,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Handle incoming request."""
        self.total_requests += 1
        
        print(f"\n[REQ] {method} {path}  client={api_key}")
        
        # Step 1: Rate limiting
        if not self.rate_limiter.is_allowed(api_key):
            self.rate_limited_requests += 1
            print(f"      -> RATE LIMITED ({self.rate_limiter.requests_per_minute}/min) — 429 Too Many Requests")
            
            return {
                'status': 429,
                'error': 'Too Many Requests',
                'message': f"Rate limit exceeded ({self.rate_limiter.requests_per_minute} requests/min)",
            }
        
        # Step 2: Check cache (for GET requests)
        if method == "GET":
            cached_response = self.cache.get(method, path, params)
            if cached_response:
                self.cache_hits += 1
                print(f"      -> CACHE HIT — {cached_response['status']} OK in 2ms")
                return cached_response
        
        # Step 3: Find upstream service
        upstream_url = self._find_upstream(path)
        if not upstream_url:
            print(f"      -> NO ROUTE FOUND — 404 Not Found")
            return {
                'status': 404,
                'error': 'Not Found',
                'message': f"No route found for {path}",
            }
        
        # Step 4: Route through circuit breaker
        service_name = upstream_url.replace("http://", "").split(':')[0]
        
        try:
            start_time = time.time()
            
            # Call upstream service
            response = await self.circuit_breaker_manager.get_breaker(service_name).call(
                self._proxy_request,
                method=method,
                url=upstream_url + path,
                body=body,
                params=params,
            )
            
            duration_ms = int((time.time() - start_time) * 1000)
            
            print(f"      -> PROXY to {service_name} — {response['status']} OK in {duration_ms}ms")
            
            # Cache response if GET
            if method == "GET" and response['status'] == 200:
                route = self._find_route(path)
                ttl = route.cache_ttl if route else 300
                self.cache.set(method, path, response, ttl=ttl, params=params)
            
            return response
        
        except CircuitBreakerOpenError as e:
            self.circuit_broken_requests += 1
            print(f"      -> CIRCUIT OPEN ({service_name}) — 503 Service Unavailable")
            
            return {
                'status': 503,
                'error': 'Service Unavailable',
                'message': str(e),
                'retry_after': 30,
            }
        
        except Exception as e:
            print(f"      -> ERROR — {e}")
            
            return {
                'status': 502,
                'error': 'Bad Gateway',
                'message': str(e),
            }
    
    async def _proxy_request(
        self,
        method: str,
        url: str,
        body: Optional[str] = None,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Proxy request to upstream service."""
        # Simulate upstream service behavior
        await asyncio.sleep(0.05 + (time.time() % 0.1))
        
        # Return mock response
        return {
            'status': 200,
            'body': {
                'data': f"Response from {url}",
                'timestamp': time.time(),
            }
        }
    
    def _find_upstream(self, path: str) -> Optional[str]:
        """Find upstream URL for path."""
        for prefix, route in self.routes.items():
            if path.startswith(prefix):
                return route.upstream_url
        return None
    
    def _find_route(self, path: str) -> Optional[Route]:
        """Find route for path."""
        for prefix, route in self.routes.items():
            if path.startswith(prefix):
                return route
        return None
    
    async def get_health_dashboard(self) -> Dict[str, Any]:
        """Get health status dashboard."""
        cache_stats = self.cache.get_cache_stats()
        
        services = {}
        for service_name, breaker_status in self.circuit_breaker_manager.get_all_status().items():
            services[service_name] = {
                'status': 'UP' if breaker_status['state'] == 'CLOSED' else 'DOWN',
                'circuit_state': breaker_status['state'],
                'failure_count': breaker_status['failure_count'],
            }
        
        return {
            'gateway_uptime': time.time(),
            'total_requests': self.total_requests,
            'rate_limited_requests': self.rate_limited_requests,
            'circuit_broken_requests': self.circuit_broken_requests,
            'cache_stats': cache_stats,
            'services': services,
        }


# Mock function for testing
async def run_gateway():
    """Run the gateway (for demo purposes)."""
    gateway = APIGateway()
    
    # Register routes
    gateway.add_route("/api/users", "http://user-service:3001", cache_ttl=60)
    gateway.add_route("/api/orders", "http://order-service:3002", cache_ttl=120)
    gateway.add_route("/api/products", "http://product-service:3003", cache_ttl=300)
    
    print(f"\n[INFO] API Gateway running on http://{gateway.host}:{gateway.port}")
    
    return gateway
