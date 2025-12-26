import os
import json
from app.logging_config import backend_logger as logger

async def get_secret(secret_name: str) -> str:
    """
    Retrieves a secret directly from environment variables.
    Maintains async signature for compatibility with the rest of the app.
    """
    value = os.getenv(secret_name)

    if value is not None:
        # distinct log to verify it's pulling from env
        logger.info(f"✅ Serving secret '{secret_name}' from environment variable.") 
        return value
    
    error_msg = f"❌ Secret '{secret_name}' not found in environment variables."
    logger.error(error_msg)
    raise ValueError(error_msg)

async def get_json_secret(secret_name: str) -> dict:
    """
    Helper function to get a secret and parse it as JSON immediately.
    """
    secret_str = await get_secret(secret_name)
    try:
        return json.loads(secret_str)
    except json.JSONDecodeError as e:
        logger.error(f"❌ Failed to decode JSON for secret '{secret_name}': {e}")
        raise