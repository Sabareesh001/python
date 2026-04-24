"""
API Gateway example with rate limiting, caching, and circuit breaker.
"""

import asyncio
import random
from gateway import APIGateway
from circuit_breaker import CircuitBreakerOpenError
from tabulate import tabulate


async def simulate_requests():
    """Simulate client requests to the gateway."""
    
    print("=" * 80)
    print("ASYNC API GATEWAY WITH RATE LIMITING, CACHING, & CIRCUIT BREAKER")
    print("=" * 80)
    
    # Create gateway
    gateway = APIGateway()
    
    # Register routes
    gateway.add_route("/api/users", "http://user-service:3001", cache_ttl=60)
    gateway.add_route("/api/orders", "http://order-service:3002", cache_ttl=120)
    gateway.add_route("/api/products", "http://product-service:3003", cache_ttl=300)
    
    print(f"\n[INFO] API Gateway initialized on http://{gateway.host}:{gateway.port}\n")
    
    # Simulate various request scenarios
    scenarios = [
        # Cache hit scenario
        ("GET", "/api/products/42", "api_key_9x3f", None),
        ("GET", "/api/products/42", "api_key_9x3f", None),  # Should be cached
        
        # Rate limiting scenario
        *[
            ("GET", f"/api/users/{i}", "api_key_9x3f", None)
            for i in range(55)  # Exceed 50/min limit
        ],
        
        # Circuit breaker scenario
        ("GET", "/api/orders/7891", "api_key_m4n1", None),
        ("GET", "/api/orders/7892", "api_key_m4n1", None),
        ("GET", "/api/orders/7893", "api_key_m4n1", None),
        ("GET", "/api/orders/7894", "api_key_m4n1", None),
        ("GET", "/api/orders/7895", "api_key_m4n1", None),
        ("GET", "/api/orders/7896", "api_key_m4n1", None),  # Should open circuit
        
        # Mixed traffic
        ("GET", "/api/products/100", "api_key_b2k7", None),
        ("POST", "/api/users/signup", "api_key_b2k7", '{"name":"Alice"}'),
    ]
    
    print("=" * 80)
    print("SIMULATING REQUESTS")
    print("=" * 80)
    
    # Process requests
    for i, (method, path, api_key, body) in enumerate(scenarios):
        await gateway.handle_request(method, path, api_key, body)
        await asyncio.sleep(0.1)  # Small delay between requests
    
    # Simulate service failures for circuit breaker
    print("\n\n" + "=" * 80)
    print("SIMULATING SERVICE FAILURES (CIRCUIT BREAKER TEST)")
    print("=" * 80)
    
    # Force failures by making the upstream call fail
    for i in range(5):
        try:
            # Simulate failure
            await gateway.handle_request(
                "GET",
                "/api/orders/1000",
                "api_key_stress_test",
                None
            )
        except Exception:
            pass
        await asyncio.sleep(0.05)
    
    # Print dashboard
    print("\n\n" + "=" * 80)
    print("HEALTH DASHBOARD")
    print("=" * 80)
    
    dashboard = await gateway.get_health_dashboard()
    
    print(f"\nGateway Stats:")
    print(f"  - Total Requests: {dashboard['total_requests']}")
    print(f"  - Rate Limited: {dashboard['rate_limited_requests']}")
    print(f"  - Circuit Broken: {dashboard['circuit_broken_requests']}")
    
    print(f"\nCache Stats:")
    cache = dashboard['cache_stats']
    print(f"  - Total Entries: {cache['total_entries']}")
    print(f"  - Cache Hits: {cache['total_hits']}")
    print(f"  - Cache Misses: {cache['total_misses']}")
    print(f"  - Hit Rate: {cache['hit_rate']}")
    
    print(f"\nDownstream Services:")
    rows = []
    for service, status in dashboard['services'].items():
        rows.append([
            service,
            status['status'],
            status['circuit_state'],
            status['failure_count'],
        ])
    
    headers = ["Service", "Status", "Circuit", "Failures"]
    print(tabulate(rows, headers=headers, tablefmt="grid"))
    
    # Rate limiter stats
    print("\n" + "=" * 80)
    print("RATE LIMITER STATS (Per API Key)")
    print("=" * 80)
    print()
    
    api_keys = ["api_key_9x3f", "api_key_b2k7", "api_key_m4n1"]
    rows = []
    for api_key in api_keys:
        stats = gateway.rate_limiter.get_client_stats(api_key)
        rows.append([
            stats['client_id'],
            stats['limit'],
            stats['remaining'],
            f"{stats['reset_in_seconds']:.0f}s" if stats['reset_in_seconds'] > 0 else "Ready",
        ])
    
    headers = ["API Key", "Limit/min", "Remaining", "Reset"]
    print(tabulate(rows, headers=headers, tablefmt="grid"))
    
    print("\n" + "=" * 80)
    print("Demo Complete!")
    print("=" * 80)


if __name__ == "__main__":
    asyncio.run(simulate_requests())
