"""
Phiversity Rate Limiter - API rate limiting and quota management

This module provides:
1. Token bucket rate limiting
2. User-based rate limits
3. IP-based rate limits
4. Endpoint-specific limits
5. Quota management
6. Rate limit headers

Author: Phiversity Team
"""

import time
import hashlib
from typing import Dict, Optional, Callable
from dataclasses import dataclass, field
from functools import wraps
from collections import defaultdict
import threading


@dataclass
class RateLimitConfig:
    """Rate limit configuration."""
    requests: int  # Number of requests
    window: float  # Time window in seconds
    burst: int = 0  # Burst allowance


@dataclass
class RateLimitState:
    """Current rate limit state."""
    tokens: float
    last_update: float
    requests_count: int = 0


class TokenBucket:
    """Token bucket algorithm implementation."""
    
    def __init__(self, capacity: int, refill_rate: float):
        self.capacity = capacity
        self.refill_rate = refill_rate  # tokens per second
        self.tokens = float(capacity)
        self.last_refill = time.time()
        self.lock = threading.Lock()
    
    def consume(self, tokens: int = 1) -> bool:
        """Try to consume tokens."""
        with self.lock:
            self._refill()
            
            if self.tokens >= tokens:
                self.tokens -= tokens
                return True
            return False
    
    def _refill(self):
        """Refill tokens based on elapsed time."""
        now = time.time()
        elapsed = now - self.last_refill
        
        # Add tokens based on elapsed time
        new_tokens = elapsed * self.refill_rate
        self.tokens = min(self.capacity, self.tokens + new_tokens)
        self.last_refill = now
    
    def get_available(self) -> float:
        """Get available tokens."""
        with self.lock:
            self._refill()
            return self.tokens


class SlidingWindow:
    """Sliding window rate limiting."""
    
    def __init__(self, max_requests: int, window_seconds: float):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests: Dict[str, list] = defaultdict(list)
        self.lock = threading.Lock()
    
    def is_allowed(self, key: str) -> bool:
        """Check if request is allowed."""
        with self.lock:
            now = time.time()
            window_start = now - self.window_seconds
            
            # Remove old requests
            self.requests[key] = [t for t in self.requests[key] if t > window_start]
            
            # Check limit
            if len(self.requests[key]) >= self.max_requests:
                return False
            
            # Add current request
            self.requests[key].append(now)
            return True
    
    def get_remaining(self, key: str) -> int:
        """Get remaining requests."""
        with self.lock:
            now = time.time()
            window_start = now - self.window_seconds
            
            recent = [t for t in self.requests[key] if t > window_start]
            
            return max(0, self.max_requests - len(recent))
    
    def get_reset_time(self, key: str) -> float:
        """Get time until reset."""
        with self.lock:
            if not self.requests[key]:
                return 0
            
            oldest = min(self.requests[key])
            return oldest + self.window_seconds - time.time()


class RateLimiter:
    """Main rate limiter class."""
    
    # Default rate limits
    DEFAULTS = {
        'global': RateLimitConfig(requests=100, window=60),
        'user': RateLimitConfig(requests=20, window=60),
        'ip': RateLimitConfig(requests=50, window=60),
    }
    
    # Endpoint-specific limits
    ENDPOINT_LIMITS = {
        '/api/run': RateLimitConfig(requests=10, window=300),  # Video generation
        '/api/jobs': RateLimitConfig(requests=30, window=60),
        '/api/health': RateLimitConfig(requests=1000, window=60),
    }
    
    def __init__(self):
        self.limiters: Dict[str, SlidingWindow] = {}
        self.user_quotas: Dict[int, Dict] = {}
        self.blocked_ips: Dict[str, float] = {}
        self.lock = threading.Lock()
        
        # Initialize limiters
        self._init_limiters()
    
    def _init_limiters(self):
        """Initialize rate limiters."""
        # Global limiter
        self.limiters['global'] = SlidingWindow(
            self.DEFAULTS['global'].requests,
            self.DEFAULTS['global'].window
        )
        
        # IP-based limiter
        self.limiters['ip'] = SlidingWindow(
            self.DEFAULTS['ip'].requests,
            self.DEFAULTS['ip'].window
        )
    
    def check_rate_limit(
        self, 
        user_id: Optional[int] = None,
        ip: Optional[str] = None,
        endpoint: Optional[str] = None
    ) -> Dict:
        """
        Check rate limit for request.
        
        Returns dict with:
        - allowed: bool
        - remaining: int
        - reset: float
        - limit: int
        """
        now = time.time()
        
        # Check if IP is blocked
        if ip and ip in self.blocked_ips:
            if self.blocked_ips[ip] > now:
                return {
                    'allowed': False,
                    'remaining': 0,
                    'reset': self.blocked_ips[ip] - now,
                    'limit': 0,
                    'reason': 'blocked'
                }
            else:
                del self.blocked_ips[ip]
        
        # Get endpoint limit or use default
        limit_config = self.ENDPOINT_LIMITS.get(endpoint, self.DEFAULTS['user'])
        
        # Build key
        keys = []
        if user_id:
            keys.append(f"user:{user_id}")
        if ip:
            keys.append(f"ip:{ip}")
        
        # Check all applicable limits
        results = []
        for key in keys:
            if key.startswith('user:'):
                limiter = self.limiters.get('user')
                if not limiter:
                    self.limiters['user'] = SlidingWindow(
                        limit_config.requests,
                        limit_config.window
                    )
                    limiter = self.limiters['user']
            else:
                limiter = self.limiters['ip']
            
            allowed = limiter.is_allowed(key)
            remaining = limiter.get_remaining(key)
            reset = limiter.get_reset_time(key)
            
            results.append({
                'key': key,
                'allowed': allowed,
                'remaining': remaining,
                'reset': reset,
                'limit': limit_config.requests
            })
        
        # If no user/IP limits, check global
        if not results:
            global_limiter = self.limiters.get('global')
            if global_limiter:
                allowed = global_limiter.is_allowed('global')
                results.append({
                    'key': 'global',
                    'allowed': allowed,
                    'remaining': global_limiter.get_remaining('global'),
                    'reset': global_limiter.get_reset_time('global'),
                    'limit': self.DEFAULTS['global'].requests
                })
        
        # Combine results (all must be allowed)
        overall_allowed = all(r['allowed'] for r in results)
        min_remaining = min(r['remaining'] for r in results) if results else 0
        max_reset = max(r['reset'] for r in results) if results else 0
        limit = results[0]['limit'] if results else 0
        
        return {
            'allowed': overall_allowed,
            'remaining': min_remaining,
            'reset': max_reset,
            'limit': limit,
            'details': results
        }
    
    def block_ip(self, ip: str, duration: float = 300):
        """Block IP address."""
        with self.lock:
            self.blocked_ips[ip] = time.time() + duration
    
    def set_user_quota(self, user_id: int, quota: Dict):
        """Set user quota."""
        with self.lock:
            self.user_quotas[user_id] = quota
    
    def check_quota(self, user_id: int, resource: str, amount: int = 1) -> bool:
        """Check if user has quota for resource."""
        with self.lock:
            if user_id not in self.user_quotas:
                return True  # No quota set, allow
            
            quota = self.user_quotas[user_id]
            
            if resource not in quota:
                return True
            
            remaining = quota[resource].get('remaining', 0)
            return remaining >= amount
    
    def consume_quota(self, user_id: int, resource: str, amount: int = 1) -> bool:
        """Consume user quota."""
        with self.lock:
            if user_id not in self.user_quotas:
                return True
            
            quota = self.user_quotas[user_id]
            
            if resource not in quota:
                return True
            
            if self.check_quota(user_id, resource, amount):
                quota[resource]['remaining'] -= amount
                return True
            
            return False


# Rate limit decorator
def rate_limit(
    requests: int = 20,
    window: float = 60,
    key_func: Optional[Callable] = None
):
    """Decorator to rate limit a function."""
    limiter = RateLimiter()
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate key
            if key_func:
                key = key_func(*args, **kwargs)
            else:
                key = f"{func.__module__}.{func.__name__}"
            
            # Check rate limit
            result = limiter.check_rate_limit(ip=key)
            
            if not result['allowed']:
                raise RateLimitExceeded(
                    f"Rate limit exceeded. Reset in {result['reset']:.1f}s"
                )
            
            return func(*args, **kwargs)
        
        return wrapper
    
    return decorator


class RateLimitExceeded(Exception):
    """Rate limit exceeded exception."""
    pass


class QuotaExceeded(Exception):
    """Quota exceeded exception."""
    pass


# Global rate limiter instance
rate_limiter = RateLimiter()


# Example usage
if __name__ == "__main__":
    limiter = RateLimiter()
    
    # Test rate limiting
    for i in range(25):
        result = limiter.check_rate_limit(ip="192.168.1.1", endpoint="/api/run")
        print(f"Request {i+1}: allowed={result['allowed']}, remaining={result['remaining']}")
    
    # Test blocking
    limiter.block_ip("10.0.0.1", duration=60)
    result = limiter.check_rate_limit(ip="10.0.0.1")
    print(f"Blocked IP: {result}")
    
    # Test quota
    limiter.set_user_quota(1, {
        'videos': {'limit': 10, 'remaining': 10},
        'storage_mb': {'limit': 1000, 'remaining': 1000}
    })
    
    print(f"Quota check: {limiter.check_quota(1, 'videos', 5)}")
    limiter.consume_quota(1, 'videos', 5)
    print(f"After consume: {limiter.check_quota(1, 'videos', 5)}")