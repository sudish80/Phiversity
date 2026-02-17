"""
Phiversity Cache Module - In-memory and disk caching

This module provides:
1. In-memory LRU cache
2. Disk-based persistent cache
3. Cache invalidation
4. TTL support
5. Cache statistics

Author: Phiversity Team
"""

import time
import json
import hashlib
import pickle
from pathlib import Path
from typing import Any, Optional, Dict, Callable
from collections import OrderedDict
from functools import wraps
from dataclasses import dataclass, field


@dataclass
class CacheEntry:
    """Single cache entry."""
    value: Any
    created_at: float
    ttl: Optional[float] = None
    hits: int = 0
    
    def is_expired(self) -> bool:
        """Check if entry has expired."""
        if self.ttl is None:
            return False
        return time.time() - self.created_at > self.ttl


class MemoryCache:
    """In-memory LRU cache with TTL support."""
    
    def __init__(self, max_size: int = 1000, default_ttl: float = 3600):
        self.cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self.max_size = max_size
        self.default_ttl = default_ttl
        self.stats = {'hits': 0, 'misses': 0, 'evictions': 0}
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        if key not in self.cache:
            self.stats['misses'] += 1
            return None
        
        entry = self.cache[key]
        
        # Check expiration
        if entry.is_expired():
            del self.cache[key]
            self.stats['misses'] += 1
            return None
        
        # Update hit count and move to end (LRU)
        entry.hits += 1
        self.cache.move_to_end(key)
        self.stats['hits'] += 1
        
        return entry.value
    
    def set(self, key: str, value: Any, ttl: Optional[float] = None):
        """Set value in cache."""
        # Evict oldest if at capacity
        if len(self.cache) >= self.max_size and key not in self.cache:
            self.cache.popitem(last=False)
            self.stats['evictions'] += 1
        
        self.cache[key] = CacheEntry(
            value=value,
            created_at=time.time(),
            ttl=ttl or self.default_ttl
        )
        self.cache.move_to_end(key)
    
    def delete(self, key: str):
        """Delete key from cache."""
        if key in self.cache:
            del self.cache[key]
    
    def clear(self):
        """Clear all cache."""
        self.cache.clear()
        self.stats = {'hits': 0, 'misses': 0, 'evictions': 0}
    
    def cleanup_expired(self):
        """Remove expired entries."""
        expired_keys = [
            key for key, entry in self.cache.items() 
            if entry.is_expired()
        ]
        for key in expired_keys:
            del self.cache[key]
    
    def get_stats(self) -> Dict:
        """Get cache statistics."""
        total = self.stats['hits'] + self.stats['misses']
        hit_rate = self.stats['hits'] / total if total > 0 else 0
        return {
            'size': len(self.cache),
            'max_size': self.max_size,
            'hits': self.stats['hits'],
            'misses': self.stats['misses'],
            'evictions': self.stats['evictions'],
            'hit_rate': f"{hit_rate:.2%}"
        }


class DiskCache:
    """Disk-based persistent cache."""
    
    def __init__(self, cache_dir: Path = Path(".cache"), max_size_mb: int = 100):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.max_size_bytes = max_size_mb * 1024 * 1024
        self._index_file = self.cache_dir / "index.json"
        self._load_index()
    
    def _load_index(self):
        """Load cache index."""
        if self._index_file.exists():
            self.index = json.loads(self._index_file.read_text())
        else:
            self.index = {}
    
    def _save_index(self):
        """Save cache index."""
        self._index_file.write_text(json.dumps(self.index, indent=2))
    
    def _get_file_path(self, key: str) -> Path:
        """Get file path for key."""
        key_hash = hashlib.md5(key.encode()).hexdigest()
        return self.cache_dir / f"{key_hash}.cache"
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from disk cache."""
        if key not in self.index:
            return None
        
        file_path = self._get_file_path(key)
        if not file_path.exists():
            del self.index[key]
            self._save_index()
            return None
        
        try:
            data = pickle.loads(file_path.read_bytes())
            
            # Check expiration
            if data.get('ttl') and time.time() - data['created_at'] > data['ttl']:
                self.delete(key)
                return None
            
            return data['value']
        except Exception:
            return None
    
    def set(self, key: str, value: Any, ttl: Optional[float] = None):
        """Set value in disk cache."""
        file_path = self._get_file_path(key)
        
        data = {
            'value': value,
            'created_at': time.time(),
            'ttl': ttl
        }
        
        try:
            file_path.write_bytes(pickle.dumps(data))
            self.index[key] = {
                'file': file_path.name,
                'size': file_path.stat().st_size,
                'created': data['created_at']
            }
            self._save_index()
            self._enforce_size_limit()
        except Exception as e:
            print(f"Cache write error: {e}")
    
    def delete(self, key: str):
        """Delete key from cache."""
        if key in self.index:
            file_path = self._get_file_path(key)
            if file_path.exists():
                file_path.unlink()
            del self.index[key]
            self._save_index()
    
    def clear(self):
        """Clear all disk cache."""
        for file in self.cache_dir.glob("*.cache"):
            file.unlink()
        self.index = {}
        self._save_index()
    
    def _enforce_size_limit(self):
        """Enforce maximum cache size."""
        total_size = sum(entry['size'] for entry in self.index.values())
        
        if total_size > self.max_size_bytes:
            # Remove oldest entries
            sorted_items = sorted(
                self.index.items(), 
                key=lambda x: x[1]['created']
            )
            
            for key, entry in sorted_items:
                if total_size <= self.max_size_bytes * 0.8:
                    break
                self.delete(key)
                total_size -= entry['size']


class CacheManager:
    """Unified cache manager with memory and disk layers."""
    
    def __init__(self):
        self.memory = MemoryCache(max_size=1000, default_ttl=3600)
        self.disk = DiskCache(cache_dir=Path(".cache/phiversity"))
    
    def get(self, key: str, use_disk: bool = True) -> Optional[Any]:
        """Get from cache (memory first, then disk)."""
        # Try memory first
        value = self.memory.get(key)
        if value is not None:
            return value
        
        # Try disk
        if use_disk:
            value = self.disk.get(key)
            if value is not None:
                # Promote to memory
                self.memory.set(key, value)
                return value
        
        return None
    
    def set(self, key: str, value: Any, ttl: Optional[float] = None, 
            use_disk: bool = True):
        """Set in cache (both memory and disk)."""
        self.memory.set(key, value, ttl)
        if use_disk:
            self.disk.set(key, value, ttl)
    
    def delete(self, key: str):
        """Delete from all cache layers."""
        self.memory.delete(key)
        self.disk.delete(key)
    
    def clear(self):
        """Clear all caches."""
        self.memory.clear()
        self.disk.clear()
    
    def get_stats(self) -> Dict:
        """Get combined cache statistics."""
        return {
            'memory': self.memory.get_stats(),
            'disk': {
                'entries': len(self.disk.index),
                'cache_dir': str(self.disk.cache_dir)
            }
        }


# Decorator for caching function results
def cached(ttl: float = 3600, key_func: Optional[Callable] = None):
    """Decorator to cache function results."""
    def decorator(func):
        cache = CacheManager()
        
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                cache_key = f"{func.__module__}.{func.__name__}:{str(args)}:{str(kwargs)}"
            
            # Try to get from cache
            result = cache.get(cache_key)
            if result is not None:
                return result
            
            # Call function and cache result
            result = func(*args, **kwargs)
            cache.set(cache_key, result, ttl)
            return result
        
        # Expose cache for debugging
        wrapper.cache = cache
        return wrapper
    
    return decorator


# Global cache instance
cache = CacheManager()


# Example usage
if __name__ == "__main__":
    # Test memory cache
    memory_cache = MemoryCache(max_size=100)
    
    memory_cache.set("test1", {"data": "value1"}, ttl=10)
    print(f"Get test1: {memory_cache.get('test1')}")
    print(f"Stats: {memory_cache.get_stats()}")
    
    # Test disk cache
    disk_cache = DiskCache()
    disk_cache.set("test2", {"data": "value2"}, ttl=60)
    print(f"Get test2: {disk_cache.get('test2')}")
    
    # Test unified cache
    cache_manager = CacheManager()
    cache_manager.set("test3", {"data": "value3"})
    print(f"Get test3: {cache_manager.get('test3')}")
    print(f"Stats: {cache_manager.get_stats()}")