import os
import re
from app.logging_config import backend_logger as logger
from cryptography.fernet import Fernet
import hashlib
import bcrypt

class CipherManager:
    """
    A singleton class to manage the Fernet cipher. It's initialized asynchronously
    on application startup and provides a synchronous getter for the application to use.
    """
    _cipher: Fernet | None = None

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verifies a plain password against a hashed password."""
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

    @staticmethod
    def get_password_hash(password: str) -> str:
        """Hashes a password using bcrypt."""
        hashed_bytes = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        return hashed_bytes.decode('utf-8')

    @staticmethod
    def is_password_strong_enough(password: str) -> tuple[bool, str]:
        """
        Checks if the password meets the strength requirements.
        Returns a tuple: (is_strong, message)
        """
        if len(password) < 8:
            return False, "Password must be at least 8 characters long."
        if not re.search(r"[A-Z]", password):
            return False, "Password must contain at least one uppercase letter."
        if not re.search(r"[a-z]", password):
            return False, "Password must contain at least one lowercase letter."
        if not re.search(r"[0-9]", password):
            return False, "Password must contain at least one number."
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
            return False, "Password must contain at least one special character."
        return True, "Password is strong."

    @classmethod
    async def init_cipher(cls):
        """
        Asynchronously fetches the master key from Google Secret Manager and
        initializes the cipher. This should be called once on application startup.
        """
        if cls._cipher is None:
            logger.info("Initializing Fernet encryption cipher...")
            try:
                # Use your async get_secret function
                master_key = await get_secret("master_encryption_key")
                cls._cipher = Fernet(master_key.encode())
                logger.info("✅ Fernet cipher initialized successfully.")
            except Exception as e:
                logger.critical(f"❌ CRITICAL: Failed to fetch MASTER_ENCRYPTION_KEY and initialize cipher: {e}")
                # Re-raise the exception to cause the application to fail on startup
                # if the key is missing, which is a critical security failure.
                raise

    @classmethod
    def get_cipher(cls) -> Fernet:
        """
        Synchronously returns the initialized Fernet cipher instance.
        Raises a RuntimeError if the cipher has not been initialized.
        """
        if cls._cipher is None:
            # This should never happen if init_cipher() is called on startup as planned.
            raise RuntimeError(
                "CipherManager has not been initialized. "
                "Ensure init_cipher() is called on application startup."
            )
        return cls._cipher

def hash_data(data: str) -> str:
    """
    Generates a SHA-256 hash of the input data for searchable lookups.
    """
    if not isinstance(data, str):
        raise TypeError(f"hash_data expects a string, but received {type(data).__name__}")
    return hashlib.sha256(data.encode()).hexdigest()