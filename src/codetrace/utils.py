
import dill
import time

from datetime import datetime
from typing import Any, Tuple

class CodeTraceUtils:
    def __init__(self) -> None:
        pass

    @staticmethod
    def measure_time(func, *args, **kwargs) -> Tuple[Any, datetime, datetime, float]:

        time_start: datetime = datetime.now()
        function_start: float = time.perf_counter()
        result: Any = func(*args, **kwargs)
        function_end: float = time.perf_counter()
        time_end: datetime = datetime.now()

        return result, time_start, time_end, function_end - function_start
    
    @staticmethod
    def print_logs(func_name: str, time_start: datetime, time_end: datetime, duration: float, return_type: type | None):
        print(f"[CodeTrace] Function {func_name} Start at {time_start}, End at {time_end}, Time use: {duration}, Return Type: {return_type}")


class CodeTraceFile:
    def __init__(self) -> None:
        pass


    @staticmethod
    def save_input(save_to: str, auto_create_path: bool, param: dict):
        pass


    @staticmethod
    def save_result(save_to: str, auto_create_path: bool, result: Any):
        pass
