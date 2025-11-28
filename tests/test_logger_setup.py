import logging
import os
from logger_setup import setup_logger

def test_logger_setup(tmp_path):
    """
    Tests the setup_logger function to ensure it configures handlers
    and logs to the correct files at the correct levels.
    
    Args:
        tmp_path: The pytest fixture for creating temporary directories.
    """
    # Define paths for our temporary log files
    app_log = tmp_path / "test_app.log"
    debug_log = tmp_path / "test_debug.log"

    # --- Setup and Act ---
    # Configure the logger to use our temporary files
    logger = setup_logger(app_log_path=str(app_log), debug_log_path=str(debug_log))
    
    # Log messages at all levels
    logger.debug("This is a debug message.")
    logger.info("This is an info message.")
    logger.warning("This is a warning message.")
    
    # --- Assert ---
    # Check that log files were created
    assert os.path.exists(app_log)
    assert os.path.exists(debug_log)

    # Read the content of the log files
    with open(app_log, 'r') as f:
        app_log_content = f.read()
    
    with open(debug_log, 'r') as f:
        debug_log_content = f.read()

    # Verify content of app.log (INFO and higher)
    assert "This is an info message." in app_log_content
    assert "This is a warning message." in app_log_content
    assert "This is a debug message." not in app_log_content

    # Verify content of debug.log (DEBUG and higher)
    assert "This is a debug message." in debug_log_content
    assert "This is an info message." in debug_log_content
    assert "This is a warning message." in debug_log_content

    # Pytest automatically handles cleanup of the tmp_path directory
