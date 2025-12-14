# -*- coding: utf-8 -*-
"""Timer for function/code_block execute time

This module will calcutor the function or code block execting time.
"""

import time

from typing import Any, Callable, Tuple
from datetime import datetime

class CodeTraceTimer:
    """CodeTrace Timer
    """

    @staticmethod
    def measure_time(
        func: Callable[..., Any],

        *args,
        **kwargs
    ) -> Tuple[Any, datetime, datetime, float]:
        """Measure Time for function consume

        Args:
            func (Callable[..., Any]): The function need to be execute

            *args    (Any): Args...
            **kwargs (Any): Kwargs...

        Returns:
            Tuple[Any, datetime, datetime, float]: A tuple containing
                - original result
                - start time
                - end time
                - execution duration in seconds

        Example:
            >>> CodeTraceTimer.measure_time()
        """

        time_start: datetime = datetime.now()
        func_start: float    = time.perf_counter()

        results: Any = func(*args, **kwargs)

        func_end: float    = time.perf_counter()
        time_end: datetime = datetime.now()

        duration: float = func_end - func_start

        return results, time_start, time_end, duration