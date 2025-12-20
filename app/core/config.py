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
    # Raised when config is missing or invalid
    pass

class Config:
    """
    App config loaded from env.
    Required variables: 
    - OPENAI_API_KEY
    - CDATA_API_BASE
    - CDATA_USERNAME
    - CDATA_PASSWORD
    """

    def __init__(self):
        # Load and validate config from environment
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
            raise
        except Exception as e:
            logger.error(f"Unexpected error loading config: {e}")
            raise ConfigurationError(f"Failed to load config: {e}")

    # Function starts with _ to indicate this function exists to support internal behavior only.
    def _get_required_env(self, key: str) -> str:
        # Get a required env 

        value = os.getenv(key)

        if not value:
            error_msg = f"Required environment variable '{key}' is not set"
            logger.error(error_msg)
            raise ConfigurationError(error_msg)
        
        if not value.strip():
            error_msg = f"Required environment variable '{key}' is empty"
            logger.error(error_msg)
            raise ConfigurationError(error_msg)
        
        return value.strip()
    
try: 
    config = Config()
except ConfigurationError as e:
    logger.error(f"Configuration error: {e}")
    logger.error(f"Please create a .env file with required variables")
    raise
except Exception as e:
    logger.error(f"Unexpected error initializing config: {e}")
    raise