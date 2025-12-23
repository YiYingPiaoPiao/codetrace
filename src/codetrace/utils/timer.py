# -*- coding: utf-8 -*-
"""Timer utilities for measuring function and code block execution time.

This module provides high-preision timing capabilities using time.pref_counter
to measure the wall-clock duration of executable objects.
"""

import time

from typing import Any, Callable, Tuple, TypeVar
from datetime import datetime

# Define a TypeVar to preserve the return type of the decorated function.
_T = TypeVar("_T")

class CodeTraceTimer:
    """Provides static methods for measuring execution metrics."""

    @staticmethod
    def measure_time(
        func: Callable[..., _T],

        *args   : Any,
        **kwargs: Any
    ) -> Tuple[_T, datetime, datetime, float]:
        """Measures the execution time and duration of a given function.

        Args:
            func (Callable[..., _T]): The function or callable to execute.
            *args    (Any): Positional arguments to pass to the function.
            **kwargs (Any): Keyword    arguments to pass to the function.

        Returns:
            Tuple[_T, datetime, datetime, float]:
                - The original result of the function.
                - The wall-clock start time (datetime).
                - The wall-clock end time (datetime).
                - The execution duration in seconds (float) using `perf_counter`.

        Examples:
            >>> def my_func(x):
            >>>     return x * 2
            >>> 
            >>> 
            >>> result, start, end, duration = CodeTraceTimer.measure_time(
            >>>     my_func, 10
            >>> )
        """

        time_start: datetime = datetime.now()
        func_start: float    = time.perf_counter()

        results: _T = func(*args, **kwargs)

        func_end: float    = time.perf_counter()
        time_end: datetime = datetime.now()

        duration: float = func_end - func_start

        return results, time_start, time_end, duration