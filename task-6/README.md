# Async API Gateway

A production-ready reverse-proxy API gateway featuring rate limiting, response caching, circuit breaker pattern, and real-time health monitoring.

## Architecture Overview

### Core Components

1. **Rate Limiter** (`rate_limiter.py`)
   - Token bucket algorithm
   - Per-client rate limiting
   - Configurable limits (requests/minute)

2. **Response Cache** (`cache.py`)
   - Time-To-Live (TTL) expiration
   - Cache key generation from requests
   - Hit/miss statistics
   - Expired entry cleanup

3. **Circuit Breaker** (`circuit_breaker.py`)
   - Prevents cascading failures
   - Three states: CLOSED, OPEN, HALF_OPEN
   - Automatic recovery with exponential backoff
   - Per-service isolation

4. **API Gateway** (`gateway.py`)
   - Reverse proxy routing
   - Request pipeline with all features
   - Async/await support
   - Health dashboard

## Key Features

### 1. Rate Limiting (Token Bucket)

```python
rate_limiter = RateLimiter(requests_per_minute=50)

# Check if request allowed
if rate_limiter.is_allowed("api_key_9x3f"):
    # Process request
    pass
else:
    # Return 429 Too Many Requests
    pass
```

**Token Bucket Algorithm:**

- Bucket holds tokens (capacity = limit)
- Tokens refill at rate = capacity / 60 per second
- Each request consumes 1 token
- If tokens < 1, request rejected

**Example (50 req/min):**

```
Initial: 50 tokens
After 1s: 50 + 0.83 = 50.83 tokens
After 2 requests: 48.83 tokens
After 30s: 50 tokens (refilled to capacity)
After 65 requests/min: 0 tokens → 429 error
```

**Benefits:**

- Smooth rate limiting (no hard cutoffs)
- Prevents burst attacks
- Fair distribution across time
- Low memory overhead

### 2. Response Caching with TTL

```python
cache = ResponseCache()

# Check cache
cached = cache.get("GET", "/api/products/42")
if cached:
    return cached  # Cache hit

# Set cache
cache.set("GET", "/api/products/42", response, ttl=300)

# Cache stats
stats = cache.get_cache_stats()
# {'total_entries': 42, 'total_hits': 156, 'hit_rate': '85.3%'}
```

**Cache Key Generation:**

```
Method + Path + Query Params → MD5 Hash
"GET:/api/products/42?size=256&sort=name"
→ "a7f3c1b9d5e8f2g4h6i9j1k3"
```

**TTL Management:**

- Per-endpoint TTL configuration
- Automatic expiration on access
- Periodic cleanup of expired entries
- Hit/miss tracking for metrics

**Cache Invalidation Strategies:**

- Time-based: Automatic expiration
- Event-based: Manual invalidation on data changes
- Size-based: LRU eviction (not implemented in demo)

### 3. Circuit Breaker Pattern

**States:**

```
CLOSED (Normal) ─→ [Failures ≥ 5] ─→ OPEN (Reject)
    ↑                                      ↓
    └─ [Success] ← HALF_OPEN (Test) ←─ [Timeout]
```

**Implementation:**

```python
breaker = CircuitBreaker(
    failure_threshold=5,
    recovery_timeout=30,
    success_threshold=2
)

try:
    result = breaker.call(make_request, url)
except CircuitBreakerOpenError:
    return fallback_response()
```

**State Transitions:**

1. **CLOSED**: Requests pass through normally
2. **OPEN**: Requests rejected immediately (fail-fast)
3. **HALF_OPEN**: Limited requests to test recovery
   - If success_threshold reached → back to CLOSED
   - If failure → back to OPEN

**Benefits:**

- Prevents cascading failures
- Fail-fast (fast error responses)
- Automatic recovery detection
- Per-service isolation

### 4. Reverse Proxy Routing

```python
gateway.add_route("/api/users", "http://user-service:3001", cache_ttl=60)
gateway.add_route("/api/orders", "http://order-service:3002", cache_ttl=120)
gateway.add_route("/api/products", "http://product-service:3003", cache_ttl=300)

# Automatic routing:
GET /api/users/42 → user-service:3001/api/users/42
GET /api/orders/100 → order-service:3002/api/orders/100
```

**Route Matching:**

- Prefix matching (longest wins)
- Per-route TTL configuration
- Upstream URL construction

### 5. Request Processing Pipeline

```
1. Rate Limiting Check
   ↓ [Allowed?]
2. Cache Lookup (GET only)
   ↓ [Cache miss or POST/PUT/DELETE]
3. Find Upstream Service
   ↓
4. Circuit Breaker
   ↓ [CLOSED?]
5. Proxy Request
   ↓
6. Cache Response (GET only, 200 OK)
   ↓
7. Return Response
```

**Example Flow:**

```
[REQ] GET /api/products/42  client=api_key_9x3f
      → CACHE HIT (TTL: 45s remaining) — 200 OK in 2ms

[REQ] GET /api/orders/latest  client=api_key_9x3f
      → PROXY to order-service — 200 OK in 134ms

[REQ] POST /api/users/signup  client=api_key_b2k7
      → RATE LIMITED (52/50 req/min) — 429 Too Many Requests

[REQ] GET /api/orders/7891  client=api_key_m4n1
      → CIRCUIT OPEN (order-service) — 503 Service Unavailable
        Fallback: {"error": "Service temporarily unavailable", "retry_after": 30}
```

### 6. Health Dashboard

```python
dashboard = await gateway.get_health_dashboard()

# Returns:
{
    'total_requests': 1250,
    'rate_limited_requests': 15,
    'circuit_broken_requests': 42,
    'cache_stats': {
        'total_entries': 87,
        'total_hits': 1156,
        'total_misses': 94,
        'hit_rate': '92.5%'
    },
    'services': {
        'user-service': {
            'status': 'UP',
            'circuit_state': 'CLOSED',
            'failure_count': 0
        },
        'order-service': {
            'status': 'DOWN',
            'circuit_state': 'OPEN',
            'failure_count': 5
        },
        'product-service': {
            'status': 'UP',
            'circuit_state': 'CLOSED',
            'failure_count': 0
        }
    }
}
```

## Usage Examples

### Basic Setup

```python
from gateway import APIGateway

# Create gateway
gateway = APIGateway(host="0.0.0.0", port=8080)

# Register routes
gateway.add_route("/api/users", "http://user-service:3001", cache_ttl=60)
gateway.add_route("/api/orders", "http://order-service:3002", cache_ttl=120)

# Handle request
response = await gateway.handle_request(
    method="GET",
    path="/api/users/42",
    api_key="client_api_key",
    params={'include': 'profile'}
)
```

### Custom Rate Limiting

```python
# Different limits for different API tiers
class TieredRateLimiter:
    def __init__(self):
        self.free_limiter = RateLimiter(requests_per_minute=10)
        self.pro_limiter = RateLimiter(requests_per_minute=100)
        self.enterprise_limiter = RateLimiter(requests_per_minute=1000)

    def is_allowed(self, api_key: str) -> bool:
        tier = get_api_tier(api_key)
        if tier == 'free':
            return self.free_limiter.is_allowed(api_key)
        elif tier == 'pro':
            return self.pro_limiter.is_allowed(api_key)
        else:
            return self.enterprise_limiter.is_allowed(api_key)
```

### Cache Warming

```python
# Pre-populate cache with critical data
async def warm_cache(gateway):
    critical_endpoints = [
        ("/api/products/popular", 300),
        ("/api/products/trending", 300),
        ("/api/categories", 600),
    ]

    for endpoint, ttl in critical_endpoints:
        response = await gateway._proxy_request("GET", endpoint)
        gateway.cache.set("GET", endpoint, response, ttl=ttl)
```

## Performance Characteristics

### Time Complexity

- **Rate limiting check**: O(1) amortized
- **Cache lookup**: O(1) with MD5 hashing
- **Circuit breaker check**: O(1)
- **Request processing**: O(1) + proxy latency

### Space Complexity

- **Rate limiter**: O(n) where n = num unique clients
- **Response cache**: O(m) where m = num cached responses
- **Circuit breakers**: O(s) where s = num services

### Benchmarks (Typical)

| Operation            | Time     | Notes             |
| -------------------- | -------- | ----------------- |
| Cache hit            | 2ms      | Fastest path      |
| Rate limit check     | <1ms     | Token bucket      |
| Circuit breaker open | <1ms     | Fail-fast         |
| Proxy to upstream    | 50-200ms | Varies by service |

## Code Statistics

- **rate_limiter.py**: 80+ lines - Token bucket implementation
- **cache.py**: 120+ lines - TTL-based response cache
- **circuit_breaker.py**: 150+ lines - Circuit breaker states
- **gateway.py**: 180+ lines - Main gateway and routing
- **example.py**: 150+ lines - Demonstration
- **Total**: 680+ lines

## Advanced Patterns

### Load Balancing

```python
class LoadBalancedGateway(APIGateway):
    def __init__(self):
        super().__init__()
        self.service_instances = defaultdict(list)

    def _find_upstream(self, path: str) -> str:
        route = self._find_route(path)
        instances = self.service_instances.get(route.service_name, [])
        # Round-robin or least connections
        return select_instance(instances)
```

### Authentication & Authorization

```python
async def handle_request(self, method, path, api_key):
    # Verify API key
    if not verify_api_key(api_key):
        return {'status': 401, 'error': 'Unauthorized'}

    # Check permissions
    if not has_permission(api_key, path):
        return {'status': 403, 'error': 'Forbidden'}

    # Continue with normal flow
    return await self._process_request(method, path, api_key)
```

### Request/Response Transformation

```python
async def transform_request(self, request):
    # Add headers
    request.headers['X-Forwarded-For'] = client_ip
    request.headers['X-Request-ID'] = uuid.uuid4()

    # Transform body
    if request.content_type == 'application/xml':
        request.body = xml_to_json(request.body)

    return request

async def transform_response(self, response):
    # Compress large responses
    if len(response.body) > 1000:
        response.body = gzip(response.body)

    return response
```

## Learning Outcomes

✅ **Async/await patterns** in Python  
✅ **Token bucket rate limiting** algorithm  
✅ **Circuit breaker pattern** for fault tolerance  
✅ **Response caching** with TTL  
✅ **Reverse proxy concepts** and implementation  
✅ **Health monitoring** and dashboards  
✅ **Request pipeline** architecture  
✅ **Thread-safe counters** and metrics

## Best Practices

✅ **Always implement circuit breakers** for external services  
✅ **Cache GET responses only** (idempotent)  
✅ **Use stratified rate limits** by API tier  
✅ **Monitor cache hit rate** (target > 80%)  
✅ **Set appropriate TTLs** (balance freshness/performance)  
✅ **Log all rate limit/circuit breaker events**  
✅ **Implement graceful degradation** (fallback responses)

## Dependencies

```
aiohttp>=3.8.0
asyncio (built-in)
tabulate>=0.9.0
```
