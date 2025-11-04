
import os
import logging

from datetime import datetime


def setup_logger(
    name: str = 'codetrace', 
    to_console: bool = True, 
    to_file: bool = False,
    level: int = logging.INFO,
    log_dir: str = 'logs'
):
    
    logger = logging.getLogger(name=name)
    logger.setLevel(level=level)

    if logger.handlers:
        return logger
    
    formatter = logging.Formatter(
        fmt="%(asctime)s - %(levelname)s - [%(name)s] - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    if to_console:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    if to_file:
        os.makedirs(log_dir, exist_ok=True)
        log_filename = datetime.now().strftime("%Y-%m-%d_%H-%M-%S.log")
        file_path = os.path.join(log_dir, log_filename)
        file_handler = logging.FileHandler(file_path, encoding='UTF-8')
        file_handler.setFormatter(formatter)

        logger.addHandler(file_handler)
    
    return logger


if __name__ == '__main__':
    logger = setup_logger()
    logger.info("This is an information!")