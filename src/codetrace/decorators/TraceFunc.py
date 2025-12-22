# -*- coding: utf-8 -*-
"""TraceFunc decorators modules.

A decorator for tracing function calls
"""

import os
import logging
import functools

from typing import Any, Callable, List, Optional
from pathlib import Path
from datetime import datetime

from ..utils.timer import CodeTraceTimer
from ..utils.logger import setup_logger
from ..utils.config import CodeTraceConfig, TIMESTAMP, TIMESTAMP_FORMAT
from ..utils.recorder import Recorder, TraceType
from ..persistence.data_persistence import DataPersistence, SupportedType



class TraceFunc:
    """A function tracing class.
    
    This is for tracing function.

    Example:
        >>> @trace_func()
        >>> def your_func():
        >>>     # TODO
        >>>     pass
    """

    def __init__(self) -> None:
        """Initialize the TraceFunc decorator with default configurations.
        """

        # By default, set the logger to None
        self.logger: Optional[logging.Logger] = None
        self._default_config: CodeTraceConfig = CodeTraceConfig()

    def config(
        self,

        # Logging configuration
        with_logs: Optional[bool] = None,
        save_logs: Optional[bool] = None,
        logs_dir : Optional[str ] = None,

        # Saving configuration
        save_inputs: Optional[bool] = None,
        save_result: Optional[bool] = None,
        save_to    : Optional[str ] = None,

        inputs_file_name: Optional[str]       = None,
        result_file_name: Optional[List[str]] = None,

        data_format: Optional[SupportedType] = None,

        # Summary configuration
        with_summary: Optional[bool] = None,
        summary_dir : Optional[str ] = None,

        # Logger, can pass custom logger object to replace default logger object.
        logger: Optional[logging.Logger] = None
    ) -> None:
        """
        Docstring for config
        
        Args:
        """
        # Customize configurations
        updates = {
            "with_logs": with_logs,
            "save_logs": save_logs,
            "logs_dir" : logs_dir ,

            "save_inputs": save_inputs,
            "save_result": save_result,
            "save_to"    : save_to,

            "inputs_file_name": inputs_file_name,
            "result_file_name": result_file_name,

            "data_format": data_format,

            "with_summary": with_summary,
            "summary_dir" : summary_dir
        }
        for key, value in updates.items():
            # Only update non-None objects, regardless of whether the parameter is the same as the old parameter.
            if value is not None:
                setattr(self._default_config, key, value)

        # Declare logger level
        logger_level = logging.DEBUG if with_logs else logging.WARNING
        if logger:
            # If pass the logger object, then use it.
            self.logger = logger

        else:
            # When already exists logger then re-use the logger
            # Else create a new logger object by default config.
            self.logger = (
                self.logger or setup_logger(
                    level   = logger_level, 
                    to_file = self._default_config.save_logs, 
                    log_dir = self._default_config.logs_dir
                )
            )
            self.logger.setLevel(logger_level)

        if with_logs is not None or save_logs is not None or logs_dir is not None:
            # When updated new config in logger
            # setup new logger to use.
            for handler in self.logger.handlers[:]:
                self.logger.removeHandler(handler)

            self.logger = setup_logger(
                level   = logger_level, 
                to_file = self._default_config.save_logs, 
                log_dir = self._default_config.logs_dir
            )


    def __call__(
        self,

        with_logs: Optional[bool] = None,

        save_inputs: Optional[bool] = None,
        save_result: Optional[bool] = None,

        inputs_file_name: Optional[str]       = None,
        result_file_name: Optional[List[str]] = None
    ) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        """Call Function logic

        This fucntion will executes when using this decorator

        Example:
            >>> @trace_func()
            >>> def my_func():
            >>>     #TODO
            >>>     pass
        """
        def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
            """Mainly decorator for TraceFunc

            This decorator will trace the function excutes time
            and save inputs and results when it's enable.

            Otherwise, this function also will excutes that
            function provices by user, and compare two function
            results using the compare function.

            In the default compare function, will comapre
            two results md5 to verfity the results is same or not.

            Args:
                func (Callable[..., Any]): The function which decorator to.

            Returns:
            """
            @functools.wraps(func)
            def wrapper(*args, **kwargs) -> Any:
                """The wrapper
                """

                ## Step 1: Local config -> This run local config.
                # Define a "CodeTraceConfig" object in each run
                # Ensure all special config not effect to global config value.
                _config: CodeTraceConfig = self._default_config.copy() # Copy the original `_default_config` value, avoid None value to execute.

                # Below is update the current config to temp config.
                # Maybe the code look like stupid, but this for readability.
                # NOTE: Represent the use not set special value for this run when the value is None.
                if with_logs is not None:
                    _config.with_logs = with_logs
                if save_inputs is not None:
                    _config.save_inputs = save_inputs
                if save_result is not None:
                    _config.save_result = save_result
                if inputs_file_name is not None:
                    _config.inputs_file_name = inputs_file_name
                if result_file_name is not None:
                    _config.result_file_name = result_file_name

                assert self.logger is not None # !! Make PyLance stop hit error (Actually have other better method, but I lazy)
                _original_logger_level = self.logger.level # Store the original logger level to safely reset the logger level.
                
                if _config.with_logs is not None:
                    # Ensure stay original config when the decorator haven't pass any logs relate value.
                    self.logger.setLevel(
                        logging.DEBUG if _config.with_logs else logging.WARNING
                    )

                # Local variable
                func_name: str = func.__name__
                timestamp: str = datetime.now().strftime(TIMESTAMP_FORMAT)

                self.logger.info("Execute function: %s @ %s.", func_name, timestamp)

                ## Step 2: Determind target saving path is exists and valid or not.
                # Create a new folder when it does't exists
                if not os.path.isdir(_config.save_to):
                    # The top level saving path, all result will saved under this folder
                    os.makedirs(os.path.join(os.getcwd(), _config.save_to), exist_ok=True)
                parent_path: str = str(Path(_config.save_to).resolve())

                # Sub-directory for each run, Using start timastamp to split
                # This `TIMESTAMP` is generated by first import module operation
                if _config.sub_path == "":
                    _config.sub_path =\
                        self._default_config.sub_path =\
                            os.path.join(parent_path, TIMESTAMP)
                    os.makedirs(_config.sub_path, exist_ok=True)

                # Recorder Configuration
                Recorder.config(
                    dirs   = os.path.join(_config.sub_path, _config.summary_dir),
                    enable = _config.with_summary
                )

                # Create a folder for this times this function execute.
                current_path: str = os.path.join(_config.sub_path, func_name, timestamp)
                os.makedirs(current_path, exist_ok=True)

                self.logger.info("This run all outputs will saved to: %s", current_path)
                
                ## Step 3: If enable save input parameters
                # The saving operation should not be effect main flow
                # Using try block ensure the result also can return to user.
                # Only record the error in the recorder and log
                if _config.save_inputs:
                    # NOTE: try...catch are implements on next module
                    # For safely, also try on this code block.
                    try:
                        DataPersistence.save_function_inputs(
                            parent_path = current_path,
                            file_name   = _config.inputs_file_name,
                            function    = func,
                            format      = _config.data_format,

                            logger = self.logger,

                            func_args   = args,
                            func_kawrgs = kwargs
                        )
                    except Exception:
                        self.logger.error("Error processing with save %s input parameters.", func_name, exc_info=True)

                ## Step 4: Execute the user logic code.
                # The excute function will return:
                #   - Results   : User's expected results, always same as not decorator.
                #   - Time Start: Function executed starting time
                #   - Time End  : Function finished executed end time, will no return if raise any error in function.
                #   - Duration  : Function executing time
                exception: Optional[Exception] = None # Define an exception variable for more judge.
                try:
                    # Use the measure time to calcutor duration and get results.
                    results, time_start, time_end, duration = CodeTraceTimer.measure_time(func, *args, **kwargs)

                    # Logging the information
                    self.logger.debug(
                        f"\n\tFunction <{func_name}> Executed Successfully.\n"
                        f"\tStart at: {time_start},\n"
                        f"\tEnded at: {time_end},\n"
                        f"\tDuration: {duration:.2f}"
                    )

                except Exception as e:
                    # Re-Raise the exception to maintain original behavior
                    # TODO: User error handler hook
                    exception = e
                    self.logger.error("Execution function <%s> failed with exception: %s.",
                                      func_name, type(exception),
                                      exc_info=True
                                    )
                    
                    # Reset the logger level to original logger level
                    # To prevent this decorator effect main stream logger.
                    self.logger.setLevel(_original_logger_level)
                    raise


                ## Step 5: Save the exection results
                # Same as saving function inputs
                # Only log the error information on runtime
                # Make sure this flow will not effect the main logic
                if _config.save_result and exception is None:
                    # exception is None equal not Error and with results
                    try:
                        DataPersistence.save_function_result(
                            parent_path = current_path,
                            file_name   = _config.result_file_name[0],
                            func_name   = func_name,
                            format      = _config.data_format,

                            logger = self.logger,
                            result = results
                        )

                    except Exception:
                        self.logger.error("Error processing with save %s output results.", func_name, exc_info=True)


                ## Step 6: Record the Execution record into recorder
                # A basic record
                # This logic will save the running duration, start-time, end-time to a dict format.
                # TODO: Abstract the logic to a function, and let user can pass a callback function.
                record = {
                    "duration"  : duration,
                    "time-start": time_start,
                    "time-end"  : time_end
                }
                Recorder.append(
                    func_name  = func_name,
                    record     = record   ,
                    trace_type = TraceType.FUNCTION
                )

                ## Done execution: reset all config to default mode.
                # Set the logger to default level.
                self.logger.setLevel(_original_logger_level)

                return results
            return wrapper
        return decorator
    