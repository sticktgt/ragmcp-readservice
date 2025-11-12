# main.py
from readservice.processor import process_streaming
from readservice.config import get_config
import sys
import logging

logger = logging.getLogger("readservice")
CONFIG = get_config()
STOP_ON_ERROR = bool(CONFIG.get("stop_on_error", True))

def handle_uncaught_exception(exctype, value, tb):
    logger.critical("[FATAL] Uncaught exception", exc_info=(exctype, value, tb))
    # Exit code depends on configuration
    sys.exit(1 if STOP_ON_ERROR else 0)

sys.excepthook = handle_uncaught_exception

if __name__ == "__main__":
    try:
        ok = process_streaming()
        # If the pipeline signaled a fatal error, choose exit code based on configuration
        if not ok:
            if STOP_ON_ERROR:
                sys.exit(1)  # Exit with error code if configured to stop on error
            else:
                sys.exit(0)  # Exit normally if not stopping on error
    except Exception as e:
        logger.critical("[FATAL] Error in main(): %s", e, exc_info=True)
        sys.exit(1 if STOP_ON_ERROR else 0)
