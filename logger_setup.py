import logging
import sys
from typing import Optional

def setup_logger(
    app_log_path: Optional[str] = "app.log", 
    debug_log_path: Optional[str] = "debug.log"
):
    """
    Configures a logger with a console handler and two file handlers.

    Args:
        app_log_path (Optional[str]): Path for the INFO level log file. 
                                     If None, this handler is skipped.
        debug_log_path (Optional[str]): Path for the DEBUG level log file.
                                        If None, this handler is skipped.
    """
    # Get the root logger
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)  # Set the lowest level to capture all messages

    # Prevent adding handlers multiple times in interactive sessions
    if logger.hasHandlers():
        logger.handlers.clear()

    # --- Formatter ---
    debug_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    info_formatter = logging.Formatter('%(asctime)s - %(levelname)s: %(message)s')
    console_formatter = logging.Formatter('%(levelname)s: %(message)s')

    # --- Console Handler (INFO level) ---
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    # --- App Log File Handler (INFO level) ---
    if app_log_path:
        app_log_handler = logging.FileHandler(app_log_path, mode='a')
        app_log_handler.setLevel(logging.INFO)
        app_log_handler.setFormatter(info_formatter)
        logger.addHandler(app_log_handler)

    # --- Debug Log File Handler (DEBUG level) ---
    if debug_log_path:
        debug_log_handler = logging.FileHandler(debug_log_path, mode='a')
        debug_log_handler.setLevel(logging.DEBUG)
        debug_log_handler.setFormatter(debug_formatter)
        logger.addHandler(debug_log_handler)

    return logger
