# -*- coding: utf-8 -*-
"""Recorder utilities for post-execution analysis.

This modules provides the Recorder class which captures execution metadata
and handles automatic summary generation or custom callback execution
when the Python interpreter exits.
"""

import os
import json
import atexit

from enum import Enum
from typing import Any, Callable, Dict, List, Optional

from .config import CodeTraceConfig

class TraceType(Enum):
    """Enumeration of supported trace types.

    Attributes:
        FUNCTION: Repersents a record originating from a function execution.
    """
    FUNCTION = "function"

class Recorder:
    """Handles the recording and persistence of execution summaries.

    This class acts as a central registry for all execution traces. It can be
    configured to either save standard JSON summary or trigger a custom callback
    upon program termination using the `atexit` module.
    """

    # Private class-level storage for execution records.
    _records: List[Dict[str, Any]] = []

    # Tracks whether the exit handler has been registered whit atexit.
    _registered: bool = False

    # Optional user-defined callback for custom summary processing.
    _callback: Optional[Callable[[List[Dict]], None]] = None

    # Global toggle for the recording functionality
    _enable: bool = True # Default is True

    # Output directory for summary files.
    _dirs = CodeTraceConfig.summary_dir

    
    @classmethod
    def config(
        cls,

        dirs  : Optional[str ] = None,
        enable: Optional[bool] = None
    ):
        """Configuration the recorder settings.

        Args:
            dirs   (Optional[str] ): The directory path where summary files will be saved.
            enable (Optional[bool]): Whether to enable the recorder functionality.
        """
        if dirs is not None:
            cls._dirs = dirs

        if enable is not None:
            cls._enable = enable


    @classmethod
    def append(
        cls, 

        func_name : str,

        record    : Dict,
        trace_type: TraceType
    ):
        """Appends a new execution record to the internal cache.

        The record will save follow below format:
        >>> {
        >>>     "name": "my_func" ,
        >>>     "type": "function",
        >>>     "record": # a record with dict format
        >>> }

        Args:
            func_name (str) : The name of the function associated with the record.
            record    (Dict): A dictionary containing the metrics/data to record.

            trace_type (TraceType): The category of the trace (e.g., FUNCTION).

        Raises:
            TypeError: If the `record` parameter is not a dictionary.
        """
        if not isinstance(record, dict):
            raise TypeError(
                f"Expected \"record\" to be a dict, but got {type(record).__name__}"
            )

        # Append the struct param into the record.
        cls._records.append({
            "name": func_name ,
            "type": trace_type.value,

            "record": record
        })


    @classmethod
    def exit_handler(cls):
        """Processes collected records when the program exits.

        This method is automatically called by the `atexit` module. It will
        either execute a custom callback or save the records to a JSON file.
        """ 

        if not cls._enable:
            return
        
        if cls._callback is not None:
            cls._callback(cls._records)

            return  # No exec default function
        
        # Default behavior: Save to JSON summary.
        summary = {
            "total"  : len(cls._records),
            "details": cls._records
        }

        # Ensure the output directory exists before writing.
        if not os.path.exists(cls._dirs):
            os.makedirs(cls._dirs, exist_ok=True)

        file_name: str = os.path.join(cls._dirs, "summary.json")

        try:
            with open(file_name, 'w', encoding='UTF-8') as f:
                json.dump(
                    obj = summary, 
                    fp  = f,

                    ensure_ascii = False,
                    indent       = 4
                )
        except IOError:
            # Fallback to console if file writing fails during exit.
            print(f"\n[CodeTrace] Failed to save summary to {file_name}")

    
    @classmethod
    def register_exit(
        cls,
        callback: Optional[Callable[[List[Dict[str, Any]]], None]] = None
    ) -> None:
        """Registers the recorder to perform actions on program exit.

        Args:
            callback (Callable): An optional function to handle records upon exit. If 
                            provided, it replaces the default JSON saving behavior.

        Raises:
            TypeError: If the provided callback is not callable.
        """

        # Check if the callback function is valid
        if callback is not None and not callable(callback):
            raise TypeError("The provided callback must be a callable.")
        
        if callback is not None:
            cls._callback = callback
        
        if not cls._registered:
            atexit.register(cls.exit_handler)
            cls._registered = True

            