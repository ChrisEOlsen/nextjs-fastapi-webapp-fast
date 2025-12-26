import logging
import os
from logging.handlers import RotatingFileHandler

# Create a logs directory if it doesn't exist within the MCP directory structure
# Note: This assumes /mcp is the WORKDIR in the Dockerfile
LOGS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "logs")
if not os.path.exists(LOGS_DIR):
    os.makedirs(LOGS_DIR)

def create_logger(name, log_file):
    """Creates a logger with a specified name and log file, with rotation."""
    # Rotate logs every 5 MB, keeping 5 backup files
    handler = RotatingFileHandler(os.path.join(LOGS_DIR, log_file), maxBytes=5*1024*1024, backupCount=5)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)

    return logger

mcp_logger = create_logger("mcp", "mcp.log")
