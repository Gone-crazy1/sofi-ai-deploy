"""
🚀 SOFI AI MEMORY OPTIMIZATION SYSTEM
====================================

Advanced memory management for handling multiple users efficiently on Render Starter Plan.
Implements connection pooling, cache optimization, and intelligent resource management.

Created for Sofi AI - The Smart Banking Assistant
"""

import os
import gc
import psutil
import logging
import threading
import time
from functools import wraps
from typing import Dict, Any, Optional
from contextlib import contextmanager
import weakref

logger = logging.getLogger(__name__)

class MemoryOptimizer:
    """Advanced memory optimization for Sofi AI production deployment"""
    
    def __init__(self):
        self.connection_pool = {}
        self.cache = {}
        self.max_cache_size = 100  # Limit cache entries
        self.max_connections = 5   # Limit database connections
        self.cleanup_interval = 300  # 5 minutes
        self.memory_threshold = 80  # 80% memory usage threshold
        self._cleanup_thread = None
        
        # Track memory usage
        try:
            self.process = psutil.Process()
        except Exception as e:
            logger.warning(f"Could not initialize psutil process: {e}")
            self.process = None
        
        self._start_cleanup_thread()
        logger.info("🚀 Memory Optimizer initialized")
    
    def _start_cleanup_thread(self):
        """Start background cleanup thread"""
        def cleanup_worker():
            while True:
                try:
                    self.cleanup_memory()
                    time.sleep(self.cleanup_interval)
                except Exception as e:
                    logger.error(f"Cleanup thread error: {e}")
                    time.sleep(60)  # Wait before retrying
        
        self._cleanup_thread = threading.Thread(target=cleanup_worker, daemon=True)
        self._cleanup_thread.start()
        logger.info("🧹 Background memory cleanup started")
    
    def get_memory_usage(self) -> Dict[str, float]:
        """Get current memory usage statistics"""
        try:
            if not self.process:
                return {'error': 'psutil not available'}
                
            memory_info = self.process.memory_info()
            memory_percent = self.process.memory_percent()
            
            return {
                'rss_mb': memory_info.rss / 1024 / 1024,  # Resident Set Size in MB
                'vms_mb': memory_info.vms / 1024 / 1024,  # Virtual Memory Size in MB
                'percent': memory_percent,
                'cache_entries': len(self.cache),
                'connections': len(self.connection_pool)
            }
        except Exception as e:
            logger.error(f"Error getting memory usage: {e}")
            return {'error': str(e)}
    
    def cleanup_memory(self):
        """Perform comprehensive memory cleanup"""
        try:
            stats_before = self.get_memory_usage()
            
            # 1. Clear old cache entries
            self._cleanup_cache()
            
            # 2. Close idle database connections
            self._cleanup_connections()
            
            # 3. Force garbage collection
            collected = gc.collect()
            
            stats_after = self.get_memory_usage()
            
            if 'error' not in stats_before and 'error' not in stats_after:
                logger.info(f"🧹 Memory cleanup completed:")
                logger.info(f"   Before: {stats_before['rss_mb']:.1f}MB ({stats_before['percent']:.1f}%)")
                logger.info(f"   After: {stats_after['rss_mb']:.1f}MB ({stats_after['percent']:.1f}%)")
                logger.info(f"   Freed: {stats_before['rss_mb'] - stats_after['rss_mb']:.1f}MB")
                logger.info(f"   GC collected: {collected} objects")
            else:
                logger.info(f"🧹 Memory cleanup completed (GC collected: {collected} objects)")
            
        except Exception as e:
            logger.error(f"Error during memory cleanup: {e}")
    
    def _cleanup_cache(self):
        """Clean up old cache entries"""
        if len(self.cache) > self.max_cache_size:
            # Remove oldest entries (simple FIFO for now)
            items_to_remove = len(self.cache) - self.max_cache_size
            keys_to_remove = list(self.cache.keys())[:items_to_remove]
            
            for key in keys_to_remove:
                self.cache.pop(key, None)
            
            logger.info(f"🗑️ Removed {items_to_remove} cache entries")
    
    def _cleanup_connections(self):
        """Clean up idle database connections"""
        current_time = time.time()
        connections_to_remove = []
        
        for conn_id, conn_info in self.connection_pool.items():
            if current_time - conn_info.get('last_used', 0) > 300:  # 5 minutes idle
                connections_to_remove.append(conn_id)
        
        for conn_id in connections_to_remove:
            conn_info = self.connection_pool.pop(conn_id, {})
            if 'connection' in conn_info:
                try:
                    conn_info['connection'].close()
                except:
                    pass
        
        if connections_to_remove:
            logger.info(f"🔌 Closed {len(connections_to_remove)} idle connections")
    
    def monitor_memory(self, threshold: float = None) -> bool:
        """Check if memory usage is above threshold"""
        if threshold is None:
            threshold = self.memory_threshold
        
        stats = self.get_memory_usage()
        memory_percent = stats.get('percent', 0)
        
        if memory_percent > threshold:
            logger.warning(f"⚠️ High memory usage: {memory_percent:.1f}% (threshold: {threshold}%)")
            self.cleanup_memory()
            return True
        
        return False
    
    @contextmanager
    def memory_context(self, operation_name: str = "operation"):
        """Context manager to monitor memory usage during operations"""
        stats_before = self.get_memory_usage()
        start_time = time.time()
        
        try:
            yield
        finally:
            stats_after = self.get_memory_usage()
            duration = time.time() - start_time
            
            memory_diff = stats_after['rss_mb'] - stats_before['rss_mb']
            
            if memory_diff > 10:  # Log if operation used more than 10MB
                logger.warning(f"📊 {operation_name} used {memory_diff:.1f}MB in {duration:.2f}s")
                
                # Force cleanup if memory usage is high
                if stats_after['percent'] > self.memory_threshold:
                    self.cleanup_memory()


def memory_efficient(func):
    """Decorator to make functions memory-efficient"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        with memory_optimizer.memory_context(func.__name__):
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                # Force cleanup of local variables
                gc.collect()
    
    return wrapper


def singleton_connection(service_name: str):
    """Decorator to ensure singleton database connections"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            conn_id = f"{service_name}_{threading.current_thread().ident}"
            
            if conn_id in memory_optimizer.connection_pool:
                # Update last used time
                memory_optimizer.connection_pool[conn_id]['last_used'] = time.time()
                return memory_optimizer.connection_pool[conn_id]['connection']
            
            # Create new connection if not exists
            if len(memory_optimizer.connection_pool) >= memory_optimizer.max_connections:
                # Remove oldest connection
                oldest_conn = min(
                    memory_optimizer.connection_pool.items(),
                    key=lambda x: x[1].get('last_used', 0)
                )
                old_conn_info = memory_optimizer.connection_pool.pop(oldest_conn[0])
                try:
                    old_conn_info['connection'].close()
                except:
                    pass
            
            # Create new connection
            connection = func(*args, **kwargs)
            memory_optimizer.connection_pool[conn_id] = {
                'connection': connection,
                'created': time.time(),
                'last_used': time.time()
            }
            
            return connection
        
        return wrapper
    return decorator


class CacheManager:
    """Efficient caching with automatic cleanup"""
    
    def __init__(self, max_size: int = 100, ttl: int = 300):
        self.max_size = max_size
        self.ttl = ttl  # Time to live in seconds
        self.cache = {}
        self.access_times = {}
    
    def get(self, key: str) -> Optional[Any]:
        """Get item from cache"""
        if key not in self.cache:
            return None
        
        # Check if expired
        if time.time() - self.access_times.get(key, 0) > self.ttl:
            self.cache.pop(key, None)
            self.access_times.pop(key, None)
            return None
        
        # Update access time
        self.access_times[key] = time.time()
        return self.cache[key]
    
    def set(self, key: str, value: Any) -> None:
        """Set item in cache"""
        # Clean up if at max size
        if len(self.cache) >= self.max_size:
            # Remove oldest accessed item
            oldest_key = min(self.access_times.items(), key=lambda x: x[1])[0]
            self.cache.pop(oldest_key, None)
            self.access_times.pop(oldest_key, None)
        
        self.cache[key] = value
        self.access_times[key] = time.time()
    
    def clear(self) -> None:
        """Clear all cache"""
        self.cache.clear()
        self.access_times.clear()


# Global instances
memory_optimizer = MemoryOptimizer()
cache_manager = CacheManager()

# Memory monitoring functions
def log_memory_stats():
    """Log current memory statistics"""
    stats = memory_optimizer.get_memory_usage()
    logger.info(f"📊 Memory: {stats['rss_mb']:.1f}MB ({stats['percent']:.1f}%) | "
                f"Cache: {stats['cache_entries']} | Connections: {stats['connections']}")

def emergency_cleanup():
    """Emergency memory cleanup when threshold is exceeded"""
    logger.warning("🚨 Emergency memory cleanup triggered!")
    
    # Clear all caches
    cache_manager.clear()
    memory_optimizer.cache.clear()
    
    # Force garbage collection
    gc.collect()
    
    # Close excess connections
    memory_optimizer._cleanup_connections()
    
    logger.info("🚨 Emergency cleanup completed")

# Export for easy import
__all__ = [
    'memory_optimizer', 
    'cache_manager', 
    'memory_efficient', 
    'singleton_connection',
    'log_memory_stats',
    'emergency_cleanup'
]
