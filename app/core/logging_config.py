"""
Simple, color-coded logging utility.

This module provides centralized logging that:
- Uses Python's built-in logging library
- Adds color-coding by log level for easy visual scanning
- Is lightweight and easy to maintain
- Can be imported and used anywhere in the application
"""

import logging
import sys
from colorama import Fore, Style, init

# Initialize colorama for cross-platform color support
init(autoreset=True)


class ColoredFormatter(logging.Formatter):
    """Custom formatter that adds color to log levels"""
    
    COLORS = {
        'DEBUG': Fore.CYAN,
        'INFO': Fore.GREEN,
        'WARNING': Fore.YELLOW,
        'ERROR': Fore.RED,
        'CRITICAL': Fore.RED + Style.BRIGHT,
    }
    
    def format(self, record):
        """Format log record with color"""
        try:
            # Add color to the level name
            levelname = record.levelname
            if levelname in self.COLORS:
                record.levelname = f"{self.COLORS[levelname]}{levelname}{Style.RESET_ALL}"
            return super().format(record)
        except Exception as e:
            # If formatting fails, return basic format
            print(f"Logging format error: {e}", file=sys.stderr)
            return super().format(record)


def setup_logging(level=logging.INFO):
    """
    Configure logging for the entire application.
    
    Args:
        level: The logging level (default: INFO)
    
    Returns:
        The root logger instance
    """
    try:
        # Create formatter
        formatter = ColoredFormatter(
            fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Create console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        
        # Configure root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(level)
        
        # Remove existing handlers to avoid duplicates
        root_logger.handlers.clear()
        
        # Add our handler
        root_logger.addHandler(console_handler)
        
        return root_logger
        
    except Exception as e:
        print(f"Failed to setup logging: {e}", file=sys.stderr)
        raise


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for a specific module.
    
    Args:
        name: The name of the module (typically __name__)
    
    Returns:
        A configured logger instance
    """
    try:
        return logging.getLogger(name)
    except Exception as e:
        print(f"Failed to get logger for {name}: {e}", file=sys.stderr)
        raise