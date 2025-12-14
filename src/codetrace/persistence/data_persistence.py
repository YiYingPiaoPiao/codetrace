# -*- coding: utf-8 -*-
"""The Data Persistence Layer

This module will make the data persistence
The data will be save as pickle type data
"""

import os
import pickle
import inspect
import logging

from enum import Enum
from typing import Any, Callable, Dict, Tuple

class SupportedType(Enum):
    """Supported Persistence File Type

    An enum class with supported type to persistence
    value is suffers
    """
    PICKLE = '.pkl'
    JSON   = '.json'
    CSV    = '.csv'

class DataPersistence:
    """Data Persistence

    Provides static methods for saving arbitrary Python object to the
    pickle for each function inputs or/and result
    """
    @staticmethod
    def persistence_pickle(
        save_dir : str,
        file_name: str,

        data_obj: object,

        logger: logging.Logger
    ) -> None:
        """Persistence the data to `pickle` format

        Args:
            save_dir  (str): File saving target directory
            file_name (str): The file name want saving to.

            data_obj (Object): An object including all data

            logger (logging.Logger): The Logger object

        Raises:
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
            - Uses `pickle.HIGHEST_RPOTOCOL` for efficiency and compatibility.
        """
        # Determind the target parent path is exists or not
        # Prevent failed to write file due to parent does't exists.
        if not os.path.isdir(save_dir):
            logger.error("Object failed to save. Parent paht [%s] doesn't exists.", save_dir)
            raise FileNotFoundError(f"Cannot found directory {save_dir}, Please ensure that is exists.")
        
        target_path = os.path.join(save_dir, f"{file_name}{SupportedType.PICKLE.value}")
        # Use `wb` mode for writing binary pickle data.
        # This can avoid decoding/encoding erros caused by different enconding methods.
        with open(target_path, 'wb') as f:
            pickle.dump(data_obj, f, protocol=pickle.HIGHEST_PROTOCOL)
        
        logger.info("[Success] Data object saved to '%s' with format '%s'", target_path, SupportedType.PICKLE)


    @staticmethod
    def save_function_inputs(
        parent_path: str,
        file_name  : str,
        function   : Callable[..., Any],
        format     : SupportedType,

        logger: logging.Logger,

        func_args  : Tuple = (),
        func_kawrgs: Dict  = {}
    ) -> None:
        """Save Function Inputs parameters

        This static function will save the function passing
        parameters to a file with `pickle` format.

        The each object file will save under `parent_path/{input_name}.pkl`.

        Args:
            parent_path (str)        : The parent path directory for saving the file.
            file_name   (str)        : The inputs persistence file name.
            function    (Callable)   : The function which call to use.
            format      (SupportType): What the saving format user want to

            logger      (logging.Logger): The logger

            *args    (Any): Positional arguments passed to the function.
            **kwargs (Any): Keyword    arguments passed to the function.

        Returns:
            None (None): None
        """
        
        try:

            # This step can make any function parameter
            # will save to a dict format inputs
            # with any function writing style
            sig   = inspect.signature(function)
            bound = sig.bind(*func_args, **func_kawrgs)
            bound.apply_defaults()

            logger.debug("Inputs parameters: %s.", str(bound.arguments))

            match format:
                case SupportedType.PICKLE:
                    DataPersistence.persistence_pickle(
                        save_dir  = parent_path,
                        file_name = file_name  ,
                        data_obj  = bound.arguments,

                        logger = logger
                    )
                case SupportedType.JSON:
                    # TODO
                    pass
                case SupportedType.CSV:
                    # TODO
                    pass
                case _:
                    # Default is `pickle` format
                    DataPersistence.persistence_pickle(
                        save_dir  = parent_path,
                        file_name = file_name  ,
                        data_obj  = bound.arguments,

                        logger = logger
                    )

        except (TypeError, ValueError) as e:
            # Different with other error
            # Can easy to identified the root cause.
            logger.error("Error binding arguments for %s: %s.", function.__name__, e, exc_info=True)
        except Exception as e:
            logger.error("Failed to save the inputs for %s.", function.__name__, exc_info=True)

        
    @staticmethod
    def save_function_result(
        parent_path: str,
        file_name  : str,
        func_name  : str,
        format     : SupportedType,

        logger: logging.Logger,

        result: Any
    ) -> None:
        """Save function executed results

        This is a static function, will saving the function executed results.
        If the results is **None** or **Empty**
        It will also save the empty result with *passing format*.

        The each object file will save under `parent_path/{output_name}.pkl`.

        Args:
            parent_path (str)        : The parent path directory for saving the file.
            file_name   (str)        : The inputs persistence file name.
            func_name   (str)        : The function name which call to use.
            format      (SupportType): What the saving format user want to

            logger      (logging.Logger): The logger

            result      (Any): The results after function exected.

        Returns:
            None (None): None

        Raises:
            Exception: The error from `DataPersistence.persistence_pickle` function

        Examples:
            >>> from data_persistence import DataPersistence
            >>> DataPersistence.save_fucntion_result()
        """
        
        try:

            # Asseume the results is Python supported type.
            # If Python unsupport will raise error on upstream logic.
            # Still using try...catch to ensure all error will not effect the main logic.

            match format:
                case SupportedType.PICKLE:
                    DataPersistence.persistence_pickle(
                        save_dir  = parent_path,
                        file_name = file_name  ,
                        data_obj  = result     ,

                        logger = logger
                    )
                case SupportedType.JSON:
                    # TODO
                    pass
                case SupportedType.CSV:
                    # TODO
                    pass
                case _:
                    # Default is `pickle` format
                    DataPersistence.persistence_pickle(
                        save_dir  = parent_path,
                        file_name = file_name  ,
                        data_obj  = result     ,

                        logger = logger
                    )

        except Exception as e:
            logger.error("Failed to save the inputs for %s.", func_name, exc_info=True)

