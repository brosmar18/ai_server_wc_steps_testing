"""
Test script to verify logging works.
"""
import sys 
from pathlib import Path

# Add parent dir to path so we can import app
sys.path.insert(0, str(Path(__file__).parent.parent))
from app.core.logging_config import setup_logging, get_logger

def test_loggin():
    # Test all logging lvels with color coding
    print("\n" + "="*60)
    print("Testing logging System")
    print("="*60 + "\n")

    try:
        setup_logging()
        logger = get_logger("test_logging")

        logger.info("Setting up logging tests...")

        # Test all levels
        logger.debug("This is a DEBUG message (cyan)")
        logger.info("This is an INFO message (green)")
        logger.warning("This is a WARNING message (yellow)")
        logger.error("This is an ERROR message (red)")
        logger.critical("This is a CRITICAL message (bright red)")

        # Test logger from different module name
        other_logger = get_logger("another_module")
        other_logger.info("Logger works from different module names")

        print("\n" + "="*60)
        print("Loggint test completed successfully!")
        print("="*60 + "\n")

        return True
    
    except Exception as e:
        print(f"\n  Logging test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    

if __name__ == "__main__":
    success = test_loggin()
    sys.exit(0 if success else 1)