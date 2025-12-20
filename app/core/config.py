"""
Config management for the app. 
- Loading .env
- Validating required config. 
- Providing typed config objects
- Error handling for missing/invalid config
"""
import os
from dotenv import load_dotenv
from app.core.logging_config import get_logger

logger = get_logger(__name__)

class ConfigurationError(Exception):
    """
    Custom exception type. 
    This is used ONLY for config-related problems. 
    It basically says "The app failed because config is wrong". 
    """
    pass

class Config:
    """
    App config object. 
    WHen this class is created: 
    - It loads .env
    - It validates required ones.
    - If anything is missing, it fails immediately.
    """

    def __init__(self):
        """
        This method runs when we do: config = Config()

        If an expeption is raised here, the object is NOT created.
        """
        try:
            load_dotenv()
            logger.info("Loading cong from .env")
            self.OPENAI_API_KEY = self._get_required_env("OPENAI_API_KEY")
            self.CDATA_API_BASE = self._get_required_env("CDATA_API_BASE")
            self.CDATA_USERNAME = self._get_required_env("CDATA_USERNAME")
            self.CDATA_PASSWORD = self._get_required_env("CDATA_PASSWORD")

            # Create auth tuple for requests
            self.CDATA_AUTH = (self.CDATA_USERNAME, self.CDATA_PASSWORD)

            logger.info(f"Configuration loaded successfully!")
            logger.info(f"CDATA API Base: {self.CDATA_API_BASE}")
            logger.info(f"CDATA Username: {self.CDATA_USERNAME}")
        except ConfigurationError:
            """
            This means:
            - We already detected a known config problem. 
            - The error message is already correct and meaningful
            `raise` (by itself) means: "Throw the SAME exception again, unchanged".

            Important: 
            - It keeps the original error message
            - It keeps the original stack trace
            """
            raise
        except Exception as e:
            """
            This catches ANY other unexpected error: 
            - BUGS
            - Library issues
            - Typos
            - Anything we did not plan for

            We log it, then convert it into a ConfigurationError
            so the rest of the app sees a clear, consistent failure type.
            """
            logger.error(f"Unexpected error loading config: {e}")
            raise ConfigurationError(f"Failed to load config: {e}")

    # Function starts with _ to indicate this function exists to support internal behavior only.
    def _get_required_env(self, key: str) -> str:
        """
        Internal helper method. 
        The leading _ means: "This method is for internal use only.

        Purpose: 
        - Reads env variable
        - Validates it
        - Reaises an error if it's missing or empty
        """

        value = os.getenv(key)

        if not value:
            """
            This runs if: 
            - The variable does not exist
            - OR it exists but is an empty string

            We: 
            - Log the error
            - Raise ConfigurationError
            - Stop execution immediately
            """
            error_msg = f"Required environment variable '{key}' is not set"
            logger.error(error_msg)
            raise ConfigurationError(error_msg)
        
        if not value.strip():
            """
            This catches cases like: 
            KEY = " "

            .strip() removes whitespace.
            If nothing remains, it's invalid.
            """
            error_msg = f"Required environment variable '{key}' is empty"
            logger.error(error_msg)
            raise ConfigurationError(error_msg)
        
        return value.strip()
    
try: 
    """
    This runs as soon as this file is imported.
    If config is invalid:
    - The app should NOT start
    - We want to fail fast and loudly
    """
    config = Config()
except ConfigurationError as e:
    """
    Known, expected failure: 
    - Missing .env
    - Missing variables
    - Empty values
    """
    logger.error(f"Configuration error: {e}")
    logger.error(f"Please create a .env file with required variables")
    raise # Stop the app
except Exception as e:
    """
    Anything else we did not expect. 
    Still fatal.
    """
    logger.error(f"Unexpected error initializing config: {e}")
    raise