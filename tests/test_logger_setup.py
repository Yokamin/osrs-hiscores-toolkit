import logging
import os
from src.logger_setup import setup_logger
import pytest

def test_setup_logger_basic_functionality(tmp_path):
    """
    Tests that setup_logger correctly configures handlers and logs to the
    correct files at the correct levels with both app_log and debug_log enabled.
    """
    app_log_path = tmp_path / "test_app.log"
    debug_log_path = tmp_path / "test_debug.log"

    logger = setup_logger(app_log_path=str(app_log_path), debug_log_path=str(debug_log_path))
    
    logger.debug("A debug message.")
    logger.info("An info message.")
    logger.warning("A warning message.")
    logger.error("An error message.")
    
    # Verify app_log_path (INFO and higher)
    with open(app_log_path, 'r') as f:
        app_log_content = f.read()
    assert "An info message." in app_log_content
    assert "A warning message." in app_log_content
    assert "An error message." in app_log_content
    assert "A debug message." not in app_log_content

    # Verify debug_log_path (DEBUG and higher)
    with open(debug_log_path, 'r') as f:
        debug_log_content = f.read()
    assert "A debug message." in debug_log_content
    assert "An info message." in debug_log_content
    assert "A warning message." in debug_log_content
    assert "An error message." in debug_log_content

def test_setup_logger_handler_clearing(tmp_path):
    """
    Tests that calling setup_logger multiple times clears previous handlers,
    preventing duplicate log output.
    """
    app_log_path_1 = tmp_path / "test_app_1.log"
    debug_log_path_1 = tmp_path / "test_debug_1.log"
    app_log_path_2 = tmp_path / "test_app_2.log"
    debug_log_path_2 = tmp_path / "test_debug_2.log"

    # First setup
    logger1 = setup_logger(app_log_path=str(app_log_path_1), debug_log_path=str(debug_log_path_1))
    logger1.info("Message from first setup.")
    
    # Second setup - should clear handlers from first setup
    logger2 = setup_logger(app_log_path=str(app_log_path_2), debug_log_path=str(debug_log_path_2))
    logger2.info("Message from second setup.")

    # Verify only second setup's files contain the message from second setup
    with open(app_log_path_2, 'r') as f:
        content = f.read()
    assert "Message from second setup." in content
    
    # Verify first setup's files do NOT contain message from second setup
    # (they should not have received it if handlers were cleared)
    if os.path.exists(app_log_path_1):
        with open(app_log_path_1, 'r') as f:
            content = f.read()
        assert "Message from second setup." not in content

def test_setup_logger_no_app_log_file(tmp_path, capsys):
    """
    Tests that no app log file is created when app_log_path is None,
    and console logging still works.
    """
    debug_log_path = tmp_path / "test_debug.log"
    
    logger = setup_logger(app_log_path=None, debug_log_path=str(debug_log_path))
    logger.info("Console message.")
    logger.debug("Debug message.") # Should go to debug file only

    assert not os.path.exists(tmp_path / "test_app.log") # Ensure app log not created
    
    # Verify debug log still works
    with open(debug_log_path, 'r') as f:
        debug_log_content = f.read()
    assert "Debug message." in debug_log_content
    assert "Console message." in debug_log_content # Console output is also part of debug.log due to root level

def test_setup_logger_no_debug_log_file(tmp_path, capsys):
    """
    Tests that no debug log file is created when debug_log_path is None,
    and app log and console logging still work.
    """
    app_log_path = tmp_path / "test_app.log"
    
    logger = setup_logger(app_log_path=str(app_log_path), debug_log_path=None)
    logger.info("Console message.")
    logger.debug("Debug message.") # Should not appear in any file

    assert not os.path.exists(tmp_path / "test_debug.log") # Ensure debug log not created
    
    # Verify app log still works
    with open(app_log_path, 'r') as f:
        app_log_content = f.read()
    assert "Console message." in app_log_content
    assert "Debug message." not in app_log_content # Debug is lower than INFO

def test_setup_logger_no_file_logs(capsys):
    """
    Tests that no file logs are created when both app_log_path and debug_log_path are None,
    and console logging still works.
    """
    # Clear handlers before setup to ensure clean state
    # This also helps capsys capture all root logger messages
    logging.getLogger().handlers.clear() 
    
    logger = setup_logger(app_log_path=None, debug_log_path=None)
    logger.info("Only console message.")
    logger.debug("This should not be logged anywhere.") # Not logged to console at INFO level

    # Ensure no file handlers were added
    root_logger = logging.getLogger()
    file_handlers_count = sum(1 for handler in root_logger.handlers if isinstance(handler, logging.FileHandler))
    assert file_handlers_count == 0

    # Verify console output
    # capsys captures stdout/stderr
    captured = capsys.readouterr()
    assert "Only console message." in captured.out
    assert "This should not be logged anywhere." not in captured.out # Debug is lower than console INFO
