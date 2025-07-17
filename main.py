# main.py
from readservice.processor import process_streaming
import sys
import traceback
import logging

logger = logging.getLogger("readservice")

def handle_uncaught_exception(exctype, value, tb):
    logger.critical("[FATAL] Uncaught exception", exc_info=(exctype, value, tb))
    sys.exit(1)

sys.excepthook = handle_uncaught_exception

if __name__ == "__main__":
    try:
        process_streaming()
    except Exception as e:
        logger.critical("[FATAL] Error in main(): %s", e, exc_info=True)
        sys.exit(1)
