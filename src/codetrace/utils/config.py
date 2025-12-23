# -*- coding: utf-8 -*-
"""Default configuration module for the CodeTrace Library.

This module defines the global configuration settings, timestamps, and the 
CodeTraceConfig dataclass used to control the behavior of tracing, logging,
and data persistence.
"""

import copy

from typing import List
from datetime import datetime
from dataclasses import dataclass, field

from ..persistence.data_persistence import SupportedType

# The format of the timestamp, e.g., 20250230_256161.
TIMESTAMP_FORMAT: str = "%Y%m%d_%H%M%S"

# The current timestamp for each program run.
# Generated once per execution.
TIMESTAMP       : str = datetime.now().strftime(TIMESTAMP_FORMAT)

# The default name prefix for various outputs like loggers and file paths.
DEFAULT_NAME    : str = "codetrace"

@dataclass
class CodeTraceConfig:
    """Configuration settings for CodeTrace execution and persistence.

    Attributes:
        with_logs        (bool)         : Whether to enable logging. If `True`, logs at **DEBUG** level;
                                        Otherwise, logs at **WARNING** level.
        save_logs        (bool)         : If `True`, saves runtime logs to a local file.
                                        *!! NOTE: This attribute can only be set at config function.*
        logs_dir         (str)          : Directory path where log files are stored.
                                        *!! NOTE: This attribute can only be set at config function.*
        save_inputs      (bool)         : Whether to persist function arguments.
        save_result      (bool)         : Whether to persist function return values.
        save_to          (str)          : Root directory for saving all trace outputs.
                                        *!! NOTE: This attribute can only be set at config function.*
        inputs_file_name (str)          : Base filename for persisted input data.
        result_file_name (List[str])    : A list containing filenames for original and new function
                                        results (used in comparison modes.)
        data_format      (SupportedType): The format used for data persistence (e.g., Pickle).
                                        *!! NOTE: This attribute can only be set at config function.*
        with_summary     (bool)         : Whether to generate and print an execution summary.
                                        *!! NOTE: This attribute can only be set at config function.*
        summary_dir      (str)          : Directory path where summary `JSON` files are stored.
                                        *!! NOTE: This attribute can only be set at config function.*
    """

    # Logging Configuration
    with_logs: bool = True
    save_logs: bool = False   # !! NOTE: Can only be set in config function.
    logs_dir : str  = ".logs" # !! NOTE: Can only be set in config fucntion.

    # Persistence behavior
    # Basic configuration
    save_inputs: bool = True
    save_result: bool = True
    save_to    : str  = ".codetrace" # !! NOTE: Can only be set in config function.

    # Filename configuration
    inputs_file_name: str       = "inputs"
    result_file_name: List[str] = field(default_factory=lambda: ["original_result", "new_function_result"])

    # Default persistence data format
    data_format: SupportedType = SupportedType.PICKLE # !! NOTE: Can only be set in config function.
    # TODO: Support different formats for each function.
    # TODO: Support different formats for input and results.

    # Summary Configuration
    with_summary: bool = True        # !! NOTE: Can only be set in config function.
    summary_dir : str  = "summarys"  # !! NOTE: Can only be set in config function.

    # Internal path management. Private attributes
    _sub_path: str = field(default="", repr=False) # !! NOTE: This variable cannot be changes.
    @property
    def sub_path(self) -> str:
        """Gets the execution sub-path (usually the timestamp directory)"""
        return self._sub_path
    @sub_path.setter
    def sub_path(self, value: str):
        """Sets the sub-path. Can only be set once (final-like behavior)

        Args:
            value (str): The string path to set.

        Raises:
            AttributeError: If an attempt is made to change a path that has
                            already been initialized.
        """
        if self._sub_path != "":
            raise AttributeError("The \"sub_path\" attrobite os foma; amd cammpt be modified once set.")
        self._sub_path = value


    def copy(self) -> "CodeTraceConfig":
        """Creates a deep copy of the current configuration.

        This ensures that modifications to the copied object do not affect
        the original global configuration.

        Returns:
            CodeTraceConfig: A new `CodeTraceConfig` instance with identical values.
        """
        return copy.deepcopy(self)
