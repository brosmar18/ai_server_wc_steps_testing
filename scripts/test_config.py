"""
Docstring for scripts.test_config
Test script to verify config works correctly. 
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.logging_config import setup_logging, get_logger
from app.core.config import config, ConfigurationError

setup_logging()
logger = get_logger("test_config")

def test_config():
    # Test config loading
    print("\n" + "="*60)
    print("Testing Config System")
    print("="*60 + "\n")

    try:
        logger.info("Testing config access...")

        logger.info(f"API BASE URL: {config.CDATA_API_BASE}")
        logger.info(f"Username: {config.CDATA_USERNAME}")
        logger.info(f"Password: {'*' * len(config.CDATA_PASSWORD)} (hidden)")
        logger.info(f"Auth tuple: ('{config.CDATA_AUTH[0]}', '***')")

        # Verify values are not empty
        assert config.CDATA_API_BASE, "API Base is empty"
        assert config.CDATA_USERNAME, "Username is empty"
        assert config.CDATA_PASSWORD, "Password is empty"
        assert config.CDATA_AUTH, "Auth tuple is empty"

        print("\n" + "="*60)
        print("Config test completed successfully!")
        print("="*60 + "\n")

        return True
    except ConfigurationError as e:
        print(f"\n Configuration test failed: {e}")
        print("\nMake sure you have created a .env file with:")
        print("CDATA_API_BASE")
        print("CDATA_USERNAME")
        print("CDATA_PASSWORD")
        return False
    
    except AssertionError as e:
        print(f"Config validation failed: {e}")
        return False
    
    except Exception as e:
        print(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
if __name__ == "__main__":
    success = test_config()
    sys.exit(0 if success else 1)