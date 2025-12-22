# -*- coding: utf-8 -*-
"""Recorder utils

Will process recoder output and visalize the results
when exit the program.
"""

import os
import json
import atexit

from enum import Enum
from typing import Callable, Dict, List, Optional

from .config import CodeTraceConfig

class TraceType(Enum):
    """All Trace Type of this Library

    This value prevent the record is call with what type
    """
    FUNCTION = 'function'

class Recorder:
    """CodeTrace Recorder

    This is a class for recorder.
    Mainly is print and log summary on program exists.

    The file will save into the json format file.
    """

    # The list of the record, each index is a record.
    _records: List = [] 

    # This parameter will record is successful to register or not
    _registered: bool = False

    # The callback function when exit programe to process
    _callback: Optional[Callable[[List[Dict]], None]] = None

    # To determine the log is enable or not, this config includes log to console and save to json two function.
    _enable: bool = True # Default is True

    # The summary saving path, default is "summarys"
    _dirs = CodeTraceConfig.summary_dir

    
    @classmethod
    def config(
        cls,

        dirs  : Optional[str ] = None,
        enable: Optional[bool] = None
    ):
        """Config the Summary propertity

        This function will let user config and customize the recorder action.

        Args:
            dirs   (str) :
            enable (bool):
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
        """Append function of Recorder

        This function is append record into a list
        the is a cache, that will calcutor on exit.

        The record will save follow below format:
        >>> {
        >>>     "name": "my_func" ,
        >>>     "type": "function",
        >>>     "record": # a record with dict format
        >>> }

        Args:
            func_name (str) : The calling function name, for easy to search after program run.
            record    (Dict): An dict record, can customize the dict struct. The record content will return from callback
                                function from main flow.

            trace_type (TraceType): An enum, for record current record is from which type to append.

        Raises:
            TypeError: When the record format is not a dict, this function will raise the error.
        """
        if not isinstance(record, dict):
            raise TypeError("The \"reocrd\" type is not a dict, please ensure your function return correct type of record.")

        # Append the struct param into the record.
        cls._records.append({
            "name": func_name ,
            "type": trace_type.value,

            "record": record
        })


    @classmethod
    def exit_handler(cls):
        """Recorder Exiting Handler

        This function will process when the program on exit
        """

        if not cls._enable:
            return
        
        if cls._callback is not None:
            cls._callback(cls._records)

            return  # No exec default function
        
        # Default action when exit the program
        # The function will save the record into a json format output file
        summary = {
            "total"  : len(cls._records),
            "details": cls._records
        }

        file_name: str = os.path.join(cls._dirs, "summary.json")
        with open(file_name, 'w', encoding='UTF-8') as f:
            json.dump(
                obj = summary, 
                fp  = f,

                ensure_ascii = False,
                indent       = 4
            )

    
    @classmethod
    def register_exit(cls, callback: Optional[Callable] = None):
        """Register Exit Event

        Args:
            cls      (class)   : This object slef.
            callback (Callable): Callback when exit program process, default is simply handler.

        Raises:
            TypeError: Given an invalid funcation
        """

        # Check if the callback function is valid
        if callback is not None and not callable(callback):
            raise TypeError("Pass an invalid callable function.")
        
        if callback is not None:
            cls._callback = callback
        
        if not cls._registered:
            atexit.register(cls.exit_handler)
            cls._registered = True