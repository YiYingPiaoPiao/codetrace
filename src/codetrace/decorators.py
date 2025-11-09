
import os
import time
import inspect
import functools

from typing import Any, Callable, Optional
from datetime import datetime

from .utils import CodeTraceUtils, CodeTraceFile


class TraceBlock:

    def __init__(self, name: str | None = None, with_logs: bool = True) -> None:

        self.name: str = name or "TraceBlock"
        self.with_logs: bool = with_logs


    def __enter__(self) -> object:
        self.t0        : float    = time.perf_counter()
        self.time_start: datetime = datetime.now()

        if self.with_logs:
            print(f"[CodeTrace] Entering block: {self.name} at {self.time_start}")

        return self


    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
        time_end: datetime = datetime.now()
        duration: float = time.perf_counter() - self.t0

        if self.with_logs:
            print(f"[CodeTrace] Exiting block: {self.name} at {time_end}, Duration: {duration}")

        return False
    

def codetrace(func):
    def wrapper(*args, **kwargs):
        result, time_start, time_end, duration = CodeTraceUtils.measure_time(func, *args, **kwargs)

        # CodeTraceUtils.print_logs(func_name=func.__name__, time_start=time_start, time_end=time_end, duration=duration)
        return result
    
    return wrapper
    

def trace_func(
    with_log: bool = True,
    save_input: bool = False,
    save_result: bool = False,
    save_to: Optional[str] = None,
    auto_create_path: bool = True,
    on_error: Optional[Callable[[Exception], None]] = None,
    include_return_type: bool = False
):
    """Decorator for tracing function execution with optional logging and persistence.

    This decorator measures execution time, logs runtime info, and optionally
    saves inputs and outputs to file.

    Args:
        with_log: Whether to print execution logs.
        save_input: Whether to save function input arguments.
        save_result: Whether to save the function's return value.
        save_to: Path to save logs or serialized data.
        auto_create_path: Automatically create directories if they don't exist.
        on_error: Optional callback invoked if the wrapped function raises an exception.
        include_return_type: Whether to include the annotated return type in logging.

    Raises:
        RuntimeError: If saving is requested but `save_to` is not specified.
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            
            # --- Validation ---
            if (save_input or save_result) and not save_to:
                raise RuntimeError(
                    "[CodeTrace] No saving path specified while save_input/save_result is True."
                )

            # --- Trace Execution ---
            try:
                result, time_start, time_end, duration = CodeTraceUtils.measure_time(
                    func, *args, **kwargs
                )
            except Exception as e:
                # Optional error handling callback
                if on_error is not None:
                    on_error(e)
                raise
            
            # --- Logging ---
            if with_log:
                if with_log:
                    return_type = None
                    if include_return_type:
                        return_type = getattr(func, "__annotations__", {}).get("return")
                    CodeTraceUtils.print_logs(
                        func_name=func.__name__,
                        time_start=time_start,
                        time_end=time_end,
                        duration=duration,
                        return_type=return_type,
                    )

            # --- Save Input ---
            if save_input and save_to:
                sig = inspect.signature(func)
                bound = sig.bind(*args, **kwargs)
                bound.apply_defaults()
                CodeTraceFile.save_input(
                    save_to=save_to,
                    auto_create_path=auto_create_path,
                    param=bound.arguments,
                )

            # --- Save Result ---
            if save_result and save_to:
                CodeTraceFile.save_result(
                    save_to=save_to,
                    auto_create_path=auto_create_path,
                    result=result,
                )
          
            return result
        return wrapper
    return decorator


def trace_class(with_log: bool = True, **trace_kwargs):
    def decorator(cls):
        for attr_name, attr in cls.__dict__.items():
            if callable(attr) and not attr_name.startswith("__"):
                setattr(cls, attr_name, trace_func(with_log=with_log, **trace_kwargs)(attr))
        return cls
    return decorator


@trace_func(with_log=True, include_return_type=True)
def my_func(a: int, b: int) -> float:
    return a / b

if __name__ == '__main__':
    my_func(1, 2)
    my_func(a=1, b=3)

    # with TraceBlock():
    #     print(1 + 1)