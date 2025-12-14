# -*- coding: utf-8 -*-
"""Utility functions for setting up a stadard logger."""

import os
import logging

from typing import Union

from .config import DEFAULT_NAME, TIMESTAMP, CodeTraceConfig

def setup_logger(
    name: str = DEFAULT_NAME,

    level: Union[int, str] = logging.INFO,

    to_console: bool = True,
    to_file   : bool = False,

    log_dir: str = CodeTraceConfig.logs_dir
) -> logging.Logger:
    """Sets up a stadardized logger with optional console and file handlers.

    The logger prevents duplicate handlers if called multiple times with 
    the same name.

    Args:
        name       (str)            : The name of the logger to retrieve or create.
        level      (Union[int, str]): The minimum logging level (e.g., logging.INFO, logging.DEBUG, etc.)
        to_console (bool)           : If True, adds a StreamHandler to output logs to the console (stdout/stderr).
        to_file    (bool)           : If True, adds a FileHandler to output logs to file in `log_dir`
        log_dir    (str)            : The directory where log files will be saved, relative to the current working directory.

    Returns:
        logger(logging.Logger): A configured `logging.Logger` instance.
    """

    # 1. Retrieve the logger instance
    logger = logging.getLogger(name=name)
    logger.setLevel(level=level)

    # 2. prevent duplicate handlers
    # Check if the logger already has handlers attached.
    if logger.handlers:
        return logger
    
    # 3. Define the common log format
    # Example format: 2025-02-30 25:61:61 - INFO - [codetrace] - Hi there.
    formatter = logging.Formatter(
        fmt     = "%(asctime)s - %(levelname)s - [%(name)s] - %(message)s",
        datefmt = "%Y-%m-%d %H:%M:%S"
    )

    # 4. Configure console output (StreamHandler)
    if to_console:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        
        logger.addHandler(console_handler)

    # 5. Configure file output (FileHandler)
    if to_file:
        # Determine the absolute path for the log directory
        log_dir = os.path.join(os.getcwd(), log_dir)

        # Ensure the log directory exists
        if not os.path.exists(log_dir):
            os.makedirs(log_dir, exist_ok=True)

        # Use the logger name and a consistent timestamp for the log file name
        log_filename = f"{name}_{TIMESTAMP}.log"
        log_filepath = os.path.join(log_dir, log_filename)

        file_handler = logging.FileHandler(log_filepath, encoding='UTF-8')
        file_handler.setFormatter(formatter)

        logger.addHandler(file_handler)
    return logger