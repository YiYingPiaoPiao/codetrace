# -*- coding: utf-8 -*-
"""The Data Persistence Layer.

This module handles the serialization and storage of function execution data,
including input parameters and return values, primarily using the pickle format.
"""

import os
import pickle
import inspect
import logging

from enum import Enum
from typing import Any, Callable, Dict, Optional, Tuple

class SupportedType(Enum):
    """Supported persisstence file formats and their extensions.

    Attributes:
        PICKLE: Python-specific binary serialization (.pkl).
        JSON  : JavaScript Object Notation (.json).
        CSV   : Comman-Separated Values (.csv).
    """
    PICKLE = '.pkl'
    JSON   = '.json'
    CSV    = '.csv'

class DataPersistence:
    """Provides static methods for persisting Python objects.

    This class offers utilities to save function inputs and results to disk
    using various supported foramts.
    """
    @staticmethod
    def persistence_pickle(
        save_dir : str,
        file_name: str,

        data_obj: object,

        logger: logging.Logger
    ) -> None:
        """Persists a Python object to a file using the `pickle` format

        Args:
            save_dir  (str): The directory where the file will be saved.
            file_name (str): The name of the file (without extension).

            data_obj (Object): The Python object to serialize.

            logger (logging.Logger): A logging.Logger instance for status reporting.

        Raises:
            FileNotFoundError: If the specified `save_dir` does not exist.
            IOError: If there's an issue opening or writing to the file.
            pickle.PicklingError: If the object cannot be serialized.

        Examples:
            >>> data = { "key" : "value" }
            >>> DataPersistence.persistence_pickle(
            >>>     save_dir  = "/home/ubuntu/codetrace/persistence_pickle/",
            >>>     file_name = "inputs",
            >>>     data_obj  = data,
            >>>     logger    = my_logger
            >>> )

        NOTE:
            - Uses `pickle.HIGHEST_PROTOCOL` for efficiency and compatibility.
        """
        
        # Determind if the target parent path exists.
        # Prevent file writing failure due to a non-existent parent path.
        if not os.path.isdir(save_dir):
            logger.error("Save failed. Directory [%s] doesn't exists.", save_dir)
            raise FileNotFoundError(f"Directory {save_dir} not found.")
        
        target_path = os.path.join(save_dir, f"{file_name}{SupportedType.PICKLE.value}")

        try:
            # Use `wb` mode to write binary pickle data.
            # This avoids decoding/encoding errors caused by different encoding methods.
            with open(target_path, 'wb') as f:
                pickle.dump(data_obj, f, protocol=pickle.HIGHEST_PROTOCOL)
            logger.info("[Success] Data object saved to '%s' with format '%s'", target_path, SupportedType.PICKLE)
        except (IOError, pickle.PicklingError) as e:
            logger.error("Failed to persist data to %s: %s.", target_path, e)
            raise


    @staticmethod
    def save_function_inputs(
        parent_path: str,
        file_name  : str,
        function   : Callable[..., Any],
        format_type: SupportedType,

        logger: logging.Logger,

        func_args  : Optional[Tuple[Any, ...]] = None,
        func_kwargs: Optional[Dict[str, Any]]  = None
    ) -> None:
        """Captures and saves function input parameters.

        This method maps positional and keyword arguments to their parameter
        names using the function's signature before persisting the resulting
        dictionary.

        Args:
            parent_path (str)        : Root directory for saving the trace.
            file_name   (str)        : Base filename for the persisted inputs.
            function    (Callable)   : The function whose inputs are being recorded.
            format_type (SupportType): The desired persistence format.

            logger      (logging.Logger): A `logging.Logger` instance.

            *args    (Any): Positional arguments passed to the function.
            **kwargs (Any): Keyword    arguments passed to the function.
        """

        # Initialize mutable defaults safely
        args   = func_args   or ()
        kwargs = func_kwargs or {}
        
        try:
            # Map arguments to parameter names defined in the signature
            sig   = inspect.signature(function)
            bound = sig.bind(*args, **kwargs)
            bound.apply_defaults()

            logger.debug("Binding inputs for %s: %s.", function.__name__, bound.arguments)

            match format_type:
                case SupportedType.PICKLE:
                    DataPersistence.persistence_pickle(
                        save_dir  = parent_path,
                        file_name = file_name  ,
                        data_obj  = bound.arguments,

                        logger = logger
                    )
                case SupportedType.JSON:
                    # TODO (@SeeChen <leeseechen@gmail.com>): Implement JSON persistence logic.
                    logger.warning("JSON format not yet implemented.")
                case SupportedType.CSV:
                    # TODO (@SeeChen <leeseechen@gmail.com>): Implement CSV persistence logic.
                    logger.warning("CSV format not yet implemented.")
                case _:
                    # Fallback to Pickle as the default robust format.
                    DataPersistence.persistence_pickle(
                        save_dir  = parent_path,
                        file_name = file_name  ,
                        data_obj  = bound.arguments,

                        logger = logger
                    )

        except (TypeError, ValueError) as e:
            logger.error("Argument binding arguments for %s: %s.", function.__name__, e, exc_info=True)
        except Exception as e:
            logger.exception("Unexpected error saving inputs for %s.", function.__name__)

        
    @staticmethod
    def save_function_result(
        parent_path: str,
        file_name  : str,
        func_name  : str,
        format_type: SupportedType,

        logger: logging.Logger,

        result: Any
    ) -> None:
        """Saves the execution result of a function.

        This is a static function used to store the result of 
        function execution.

        If the result is **None** pr **Empty**, it will also
        store an empty result in a *specified format*.

        Args:
            parent_path (str)        : Root directory for saving the trace
            file_name   (str)        : Base filename for the persisted result.
            func_name   (str)        : Name of the function that generated the result.
            format      (SupportType): The desired persistence format.

            logger      (logging.Logger): A logging.Logger instance.

            result      (Any): The data to persist (Can be `None`)

        Returns:
            None (None): None

        Raises:
            Exception: The error from `DataPersistence.persistence_pickle` function
        """
        
        try:

            # Asseume the results is Python supported type.
            # If Python unsupport will raise error on upstream logic.
            # Still using try...catch to ensure all error will not effect the main logic.

            match format_type:
                case SupportedType.PICKLE:
                    DataPersistence.persistence_pickle(
                        save_dir  = parent_path,
                        file_name = file_name  ,
                        data_obj  = result     ,

                        logger = logger
                    )
                case SupportedType.JSON:
                    # TODO (@SeeChen <leeseechen@gmail.com>): Implement JSON persistence logic.
                    logger.warning("JSON format not yet implemented.")
                case SupportedType.CSV:
                    # TODO (@SeeChen <leeseechen@gmail.com>): Implement CSV persistence logic.
                    logger.warning("CSV format not yet implemented.")
                case _:
                    # Default is `pickle` format
                    DataPersistence.persistence_pickle(
                        save_dir  = parent_path,
                        file_name = file_name  ,
                        data_obj  = result     ,

                        logger = logger
                    )

        except Exception as e:
            logger.exception("Failed to save result for function: %s.", func_name)

