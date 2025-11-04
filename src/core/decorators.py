"""
Utility decorators for the Movistar Automation System.

Provides common decorators for:
- Retry logic with exponential backoff
- Timing/performance measurement
- Logging
- Caching
- Exception handling

Example:
    >>> @retry(max_attempts=3)
    >>> @timing
    >>> def load_file(path):
    ...     return pd.read_csv(path)
"""

import time
import logging
import functools
from typing import Callable, Any, Optional, Type
from pathlib import Path

from src.core.exceptions import RetryExhaustedError


logger = logging.getLogger(__name__)


def retry(
    max_attempts: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: tuple[Type[Exception], ...] = (Exception,),
    on_retry: Optional[Callable] = None
):
    """
    Retry decorator with exponential backoff.
    
    Args:
        max_attempts: Maximum number of retry attempts
        delay: Initial delay between retries (seconds)
        backoff: Multiplier for delay (exponential backoff)
        exceptions: Tuple of exceptions to catch
        on_retry: Optional callback function(attempt, exception) called on each retry
        
    Returns:
        Decorated function
        
    Example:
        >>> @retry(max_attempts=3, delay=1.0, backoff=2.0)
        >>> def unstable_operation():
        ...     # May fail occasionally
        ...     pass
        
    Raises:
        RetryExhaustedError: If all retry attempts fail
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            current_delay = delay
            last_exception = None
            
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                    
                except exceptions as e:
                    last_exception = e
                    
                    if attempt == max_attempts:
                        # Final attempt failed
                        break
                    
                    # Log retry
                    logger.warning(
                        f"Attempt {attempt}/{max_attempts} failed for {func.__name__}: {e}. "
                        f"Retrying in {current_delay:.1f}s..."
                    )
                    
                    # Call callback if provided
                    if on_retry:
                        on_retry(attempt, e)
                    
                    # Wait before retry
                    time.sleep(current_delay)
                    current_delay *= backoff
            
            # All retries exhausted
            raise RetryExhaustedError(
                operation=func.__name__,
                attempts=max_attempts,
                last_error=last_exception
            )
        
        return wrapper
    return decorator


def timing(func: Callable) -> Callable:
    """
    Decorator to measure execution time.
    
    Logs the execution time of the decorated function.
    
    Example:
        >>> @timing
        >>> def slow_operation():
        ...     time.sleep(2)
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        start_time = time.time()
        
        try:
            result = func(*args, **kwargs)
            elapsed = time.time() - start_time
            
            logger.info(
                f"⏱️  {func.__name__} completed in {elapsed:.2f}s"
            )
            
            return result
            
        except Exception as e:
            elapsed = time.time() - start_time
            logger.error(
                f"❌ {func.__name__} failed after {elapsed:.2f}s: {e}"
            )
            raise
    
    return wrapper


def log_execution(
    level: int = logging.INFO,
    include_args: bool = False,
    include_result: bool = False
):
    """
    Decorator to log function execution.
    
    Args:
        level: Logging level
        include_args: Log function arguments
        include_result: Log function result
        
    Example:
        >>> @log_execution(level=logging.DEBUG, include_args=True)
        >>> def process_data(data):
        ...     return data.upper()
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            # Log start
            msg = f"🔄 Executing {func.__name__}"
            
            if include_args:
                args_repr = [repr(a) for a in args]
                kwargs_repr = [f"{k}={v!r}" for k, v in kwargs.items()]
                all_args = ", ".join(args_repr + kwargs_repr)
                msg += f"({all_args})"
            
            logger.log(level, msg)
            
            try:
                result = func(*args, **kwargs)
                
                # Log success
                success_msg = f"✅ {func.__name__} completed successfully"
                if include_result:
                    success_msg += f" -> {result!r}"
                
                logger.log(level, success_msg)
                
                return result
                
            except Exception as e:
                logger.error(f"❌ {func.__name__} raised {type(e).__name__}: {e}")
                raise
        
        return wrapper
    return decorator


def catch_and_log(
    exceptions: tuple[Type[Exception], ...] = (Exception,),
    default_return: Any = None,
    reraise: bool = True
):
    """
    Decorator to catch and log exceptions.
    
    Args:
        exceptions: Tuple of exceptions to catch
        default_return: Default return value if exception occurs
        reraise: Whether to re-raise the exception after logging
        
    Example:
        >>> @catch_and_log(exceptions=(ValueError,), default_return=None)
        >>> def risky_operation():
        ...     raise ValueError("Something went wrong")
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            try:
                return func(*args, **kwargs)
            except exceptions as e:
                logger.error(
                    f"Exception in {func.__name__}: {type(e).__name__}: {e}",
                    exc_info=True
                )
                
                if reraise:
                    raise
                
                return default_return
        
        return wrapper
    return decorator


def cache_result(ttl_seconds: Optional[int] = None):
    """
    Simple in-memory cache decorator.
    
    Caches function results based on arguments.
    
    Args:
        ttl_seconds: Time-to-live in seconds (None = never expire)
        
    Example:
        >>> @cache_result(ttl_seconds=3600)
        >>> def expensive_computation(x):
        ...     time.sleep(5)
        ...     return x ** 2
    """
    def decorator(func: Callable) -> Callable:
        cache = {}
        cache_timestamps = {}
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            # Create cache key from args and kwargs
            key = str(args) + str(sorted(kwargs.items()))
            
            # Check if cached and not expired
            if key in cache:
                if ttl_seconds is None:
                    # Never expires
                    logger.debug(f"💾 Cache hit for {func.__name__}")
                    return cache[key]
                
                # Check TTL
                elapsed = time.time() - cache_timestamps[key]
                if elapsed < ttl_seconds:
                    logger.debug(
                        f"💾 Cache hit for {func.__name__} "
                        f"(age: {elapsed:.1f}s/{ttl_seconds}s)"
                    )
                    return cache[key]
                else:
                    # Expired
                    logger.debug(f"⏱️  Cache expired for {func.__name__}")
                    del cache[key]
                    del cache_timestamps[key]
            
            # Not cached or expired - compute
            logger.debug(f"🔄 Cache miss for {func.__name__} - computing")
            result = func(*args, **kwargs)
            
            # Store in cache
            cache[key] = result
            cache_timestamps[key] = time.time()
            
            return result
        
        # Add cache control methods
        wrapper.cache_clear = lambda: cache.clear()
        wrapper.cache_info = lambda: {
            "size": len(cache),
            "keys": list(cache.keys())
        }
        
        return wrapper
    return decorator


def validate_file_exists(param_name: str = "file_path"):
    """
    Decorator to validate that a file exists.
    
    Args:
        param_name: Name of the parameter containing the file path
        
    Example:
        >>> @validate_file_exists(param_name="input_file")
        >>> def process_file(input_file: Path):
        ...     pass
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            # Get file path from kwargs or args
            file_path = kwargs.get(param_name)
            
            if file_path is None and args:
                # Try to find in args by parameter name
                import inspect
                sig = inspect.signature(func)
                params = list(sig.parameters.keys())
                if param_name in params:
                    idx = params.index(param_name)
                    if idx < len(args):
                        file_path = args[idx]
            
            if file_path is not None:
                path = Path(file_path)
                if not path.exists():
                    from src.core.exceptions import FileNotFoundError
                    raise FileNotFoundError(file_path=str(path))
            
            return func(*args, **kwargs)
        
        return wrapper
    return decorator


def deprecated(reason: str, alternative: Optional[str] = None):
    """
    Mark a function as deprecated.
    
    Args:
        reason: Reason for deprecation
        alternative: Suggested alternative function
        
    Example:
        >>> @deprecated("Old implementation", alternative="new_function")
        >>> def old_function():
        ...     pass
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            message = f"⚠️  {func.__name__} is deprecated: {reason}"
            if alternative:
                message += f". Use {alternative} instead"
            
            logger.warning(message)
            
            return func(*args, **kwargs)
        
        return wrapper
    return decorator


# Export all decorators
__all__ = [
    "retry",
    "timing",
    "log_execution",
    "catch_and_log",
    "cache_result",
    "validate_file_exists",
    "deprecated",
]
