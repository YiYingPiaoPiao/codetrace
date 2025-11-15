"""
Utilities for saving Python objects (e.g., function inputs/outputs) to disk 
using the pickle format.
"""
import os
import pickle
import inspect

from typing import Any, Callable


class DataSaver:
    """
    Provides static methods for saving arbitrary Python objects to a specified 
    directory, primarily intended for functions' inputs or results.
    """

    @staticmethod
    def save_file(save_dir: str, filename_base: str, data_object: Any) -> None:
        """
        Saves a Python object to a file in the specified directory using pickle.

        Args:
            save_dir: The directory path where the file should be saved.
            filename_base: The base name for the file (e.g., function name).
            data_object: The Python object to be serialized and saved.

        Raises:
            IOError: If there's an issue opening or writing to the file.
            pickle.PicklingError: If the object cannot be serialized.
        """
        # Ensure the directory exists before attempting to save.
        os.makedirs(save_dir, exist_ok=True)
        
        file_path = os.path.join(save_dir, f"{filename_base}.pkl")

        # Use 'wb' mode for writing binary pickle data.
        with open(file_path, 'wb') as f:
            pickle.dump(data_object, f)

        # print(f"Successfully saved data to: {file_path}")

    @staticmethod
    def save_function_inputs(
        base_dir: str,
        func: Callable[..., Any],
        *args, **kwargs
    ) -> None:
        """
        Extracts and saves the bound arguments of a function call to a file.

        The arguments are saved under a subdirectory named 'input' inside base_dir.

        Args:
            base_dir: The root directory for saving data.
            func: The function being called. Used to extract its signature and name.
            *args: Positional arguments passed to the function.
            **kwargs: Keyword arguments passed to the function.
        """
        try:
            # Bind arguments to the function signature to include default values.
            sig = inspect.signature(func)
            bound = sig.bind(*args, **kwargs)
            bound.apply_defaults()
            
            # Create the dedicated 'input' subdirectory.
            save_dir = os.path.join(base_dir, "input")
            
            # The object to save is the dictionary of all bound arguments.
            DataSaver.save_file(
                save_dir=save_dir, 
                filename_base=func.__name__, 
                data_object=bound.arguments
            )

        except (TypeError, ValueError) as e:
            # Catch errors related to binding (e.g., missing required argument).
            print(f"Error binding arguments for {func.__name__}: {e}")
        except Exception as e:
            # Catch file/pickle errors.
            print(f"Error saving input for {func.__name__}: {e}")

    @staticmethod
    def save_function_results(
        base_dir: str,
        func_name: str,
        result: Any
    ) -> None:
        """
        Saves the result of a function call to a file.

        The result is saved under a subdirectory named 'output' inside base_dir.

        Args:
            base_dir: The root directory for saving data.
            func_name: The name of the function (used for the filename).
            result: The object returned by the function.
        """
        save_dir = os.path.join(base_dir, "output")
        DataSaver.save_file(
            save_dir=save_dir,
            filename_base=func_name,
            data_object=result
        )