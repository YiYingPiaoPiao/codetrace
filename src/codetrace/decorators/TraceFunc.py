# -*- coding: utf-8 -*-
"""TraceFunc decorators modules for function instrumentation.

This module provides the TraceFunc class, which can be used as a decorator
to trace function execution, log durations, and persist inputs/outputs.
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
    """A decorator class for tracing and recording function execution.

    This class provides a configurable way to log function calls, measure
    execution time, and save input/output data for debugging or auditing.

    Attributes:
        logger (logging.Logger): The logger instance used for reporting.
    """

    def __init__(self) -> None:
        """Initializes the TraceFunc with default configurations."""

        # By default, the logger is set to `None`
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
        """Updates the global configuration for the trace

        Args:
            with_logs        (Optional[bool]          ): Whether to enable logging output.
            save_logs        (Optional[bool]          ): Whether to write logs to a file.
            logs_dir         (Optional[str]           ): Directory for log files.
            save_inputs      (Optional[bool]          ): Whether to persist function input arguments.
            save_result      (Optional[bool]          ): Whether to persist function return values.
            save_to          (Optional[str]           ): Root directory for all persistence data.
            inputs_file_name (Optional[str]           ): Filename  for saved inputs.
            result_file_name (Optional[List[str]]     ): Filenames for saved results.
            data_format      (Optional[SupportedType] ): The serialization format to use (e.g., PICKLE)
            with_summary     (Optional[bool]          ): Whether to generate a summary at the end.
            summary_dir      (Optional[str]           ): Directory for summary files.
            logger           (Optional[logging.Logger]): Custom logger instance to override the default.
        """

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

        # Refreshes or creates the logger based on current config.
        logger_level = logging.DEBUG if with_logs else logging.WARNING
        if logger:
            # If a logger object is passed, use it.
            self.logger = logger

        else:
            # Re-initialize logger if settings changed or logger doesn't exist
            self.logger = (
                self.logger or setup_logger(
                    level   = logger_level, 
                    to_file = self._default_config.save_logs, 
                    log_dir = self._default_config.logs_dir
                )
            )
            self.logger.setLevel(logger_level)

        if with_logs is not None or save_logs is not None or logs_dir is not None:
            # Remove all logger handler
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
        """The core decorator for TraceFunc

        This method allows the instance to be used as a decorator
        with optional overrides.

        Args:
            with_logs        (Optional[bool]     ): Whether to enable logging output.
            save_inputs      (Optional[bool]     ): Whether to persist function input arguments.
            save_result      (Optional[bool]     ): Whether to persist function return values.
            inputs_file_name (Optional[str]      ): Filename  for saved inputs.
            result_file_name (Optional[List[str]]): Filenames for saved results.

        Returns:
            A decorator function that wraps the target function.

        Example:
            >>> @trace_func()
            >>> def my_func():
            >>>     #TODO
            >>>     return value
        """
        def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
            """The main decorator for `TraceFunc`

            Enabling this decorator will track the execution time
            of the function and save the input and results.

            Additionally, this decorator will execute the user-provided
            function and compare the results of the two functions using
            a comparison function.

            In the default comparison function, the MD5 values of the 
            two results will be used to verfiy that they are the same.

            Args:
                func (Callable[..., Any]): The function that the decorator will execute.

            Returns:
                Wrapper (Callable[..., Any]): The decorator.
            """
            @functools.wraps(func)
            def wrapper(*args, **kwargs) -> Any:
                """Main Wrapper"""

                ## Step 1: Local config -> This run uses the local configuration.
                # Define a "CodeTraceConfig" object for each run.
                # Ensure that all special configuration do not affect global configuration values.
                _config: CodeTraceConfig = self._default_config.copy()

                # The following code updates the current configuration to a temporary configuration.
                # NOTE: When the value is None, it means no special value was set for this times.
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

                assert self.logger is not None # !! Stop PyLance from throwing errors (there's actually a better way, but I'm lazy)
                _original_logger_level = self.logger.level # Store the original log level for safely reset the log level.
                
                if _config.with_logs is not None:
                    # When the decorator does not pass any log-related values
                    # Ensure that the original configuration is maintained.
                    self.logger.setLevel(
                        logging.DEBUG if _config.with_logs else logging.WARNING
                    )

                # Local variables
                func_name: str = func.__name__
                timestamp: str = datetime.now().strftime(TIMESTAMP_FORMAT)


                ## Step 2: Determine if the target save path exists and is valid.
                # If the target folder does not exists, create a new folder.
                save_root: Path = Path(_config.save_to).resolve()
                if not _config.sub_path:
                    # Initialize sub_path if first time
                    sub_path: Path = save_root / TIMESTAMP
                    sub_path.mkdir(parents=True, exist_ok=True)

                    # Setting up the sub_path to configurations.
                    _config.sub_path = str(sub_path)
                    self._default_config.sub_path = str(sub_path)

                # Generate current run path
                current_path_Path: Path = Path(_config.sub_path) / func_name / timestamp
                current_path_Path.mkdir(parents=True, exist_ok=True)
                current_path: str = str(current_path_Path)

                # Recorder Configuration
                Recorder.config(
                    dirs   = os.path.join(_config.sub_path, _config.summary_dir),
                    enable = _config.with_summary
                )

                self.logger.info("Execute function: %s @ %s.", func_name, timestamp)
                self.logger.info("All outputs from this run will be saved to: %s", current_path)
                
                ## Step 3: Enable Saving Input Parameters
                # The save operation should not affect the main flow.
                # Use a try block to ensure that the result is also returned to the user.
                # Only log errors in the logger.
                if _config.save_inputs:
                    try:
                        DataPersistence.save_function_inputs(
                            parent_path = current_path,
                            file_name   = _config.inputs_file_name,
                            function    = func,
                            format_type = _config.data_format,

                            logger = self.logger,

                            func_args   = args,
                            func_kwargs = kwargs
                        )
                    except Exception:
                        self.logger.exception("Failed to save inputs for %s.", func_name)

                ## Step 4: Excute user logic code.
                # The excute function will return:
                #   - Results   : The result expected by the user, always the same as the result returned by the *not* decorator.
                #   - Time Start: The time when the function begins execution.
                #   - Time End  : The time when the function finishes excution. If any error occrus in the function, it will not return any value.
                #   - Duration  : The execution time of the function.
                exception: Optional[Exception] = None # Define an exception variable for further judgment.
                try:
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
                    # To prevent this decorator from affecting mainstream loggers.
                    self.logger.setLevel(_original_logger_level)
                    raise


                ## Step 5: Save the exection results
                # Same as saving function input
                # Only log error information at runtime
                # Ensure this process does not affect the main logic.
                if _config.save_result and exception is None:
                    # An exception of None means there is a result and no error is repoted.
                    try:
                        DataPersistence.save_function_result(
                            parent_path = current_path,
                            file_name   = _config.result_file_name[0],
                            func_name   = func_name,
                            format_type = _config.data_format,

                            logger = self.logger,
                            result = results
                        )

                    except Exception:
                        self.logger.exception("Failed to save results for %s.", func_name)


                ## Step 6: Write the execution record to the logger
                # Basic record
                # This logic saves the execution duration, start time, and end time as a dictinory.
                # TODO: Abstract the logic into a function and allow users to pass a callback function.
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

                ## Done: All configuration are reset to default mode.
                # Set the logger to default level.
                self.logger.setLevel(_original_logger_level)

                return results
            return wrapper
        return decorator
    