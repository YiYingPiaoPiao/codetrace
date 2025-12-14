# -*- coding: utf-8 -*-
"""Default configuration module.

Docstring for codetrace.utils.config
"""

import copy

from datetime import datetime
from dataclasses import dataclass, field

from typing import List

from ..persistence.data_persistence import SupportedType

# The format of the timestamp, ex: 20250230_256161
TIMESTAMP_FORMAT: str = "%Y%m%d_%H%M%S"
# The current timestamp for each program run.
# This timestamp only generate one times for every run.
TIMESTAMP       : str = datetime.now().strftime(TIMESTAMP_FORMAT)
# The default name for all config
# Ex: logger, filepath, etc.
DEFAULT_NAME    : str = "codetrace"

@dataclass
class CodeTraceConfig:
    """Docstring for CodeTraceConfig
    """

    # When True , the decorator will log `debug`   level messages
    # When False, the decorator will log `warning` level messages
    with_logs: bool = True

    # Save the runtime log to local
    # The file will same as the terminal output.
    save_logs: bool = False # !! NOTE: Can only set in config function.

    # The logfile directory
    # In default, that will save on the `.logs` folder
    logs_dir: str = ".logs" # !! NOTE: Can only set in config fucntion.

    # Whether to save function inputs
    # In function, this is parameters
    save_inputs: bool = True

    # Whether to save function results
    # If the function is not return any value, will save the empty data object.
    save_result: bool = True

    # Default directory to save each function output.
    # Ex: inputs, results, time consume, etc.
    save_to: str = ".codetrace" # !! NOTE: Can only set in config function.

    # Default file name with input data persistence
    # This config only effect the file name, not the format
    inputs_file_name: str = "inputs"

    # Default file name with each function data persistence, uses the first name in default
    # If the decorator includes compare function, will uses the seconde file name to persistence
    result_file_name: List[str] = field(default_factory=lambda: ["original_result", "new_function_result"])

    # Default persistence data format
    # Current only support pickle
    data_format: SupportedType = SupportedType.PICKLE # !! NOTE: Can only set in config function.
    
    # TODO: Can support each function with different format
    # TODO: Can support different format on inputs and results

    # The sub-path is generate by first times function call, it's under the `save_to`
    # Ex: .codetrace/TIMESTAMP/
    _sub_path: str = field(default="", repr=False) # !! NOTE: This variable cannot be changes.
    @property
    def sub_path(self) -> str:
        return self._sub_path
    @sub_path.setter
    def sub_path(self, value: str):
        if self._sub_path != "":
            raise AttributeError("The value `sub_path` is a final attribute variable.")
        self._sub_path = value

    def copy(self) -> "CodeTraceConfig":
        """Copy function

        Ensuring the outside any operation will not effect the main config value.
        
        Returns:
            Object (CodeTraceConfig): An after deepcopy `CodeTraceConfig` Objects.
        """
        return copy.deepcopy(self)
