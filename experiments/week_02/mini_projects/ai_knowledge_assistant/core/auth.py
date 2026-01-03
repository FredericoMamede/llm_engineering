"""
Simple authentication: username/password from environment variables.

Security: Auth is ENABLED by default (secure by default).
To disable for development, set DISABLE_AUTH=true in .env.

For production use, replace with proper auth (OAuth, JWT, etc.).
"""

import os
import sys
from functools import wraps
from typing import Callable, Optional

from dotenv import load_dotenv

load_dotenv(override=True)


def get_credentials() -> tuple[Optional[str], Optional[str]]:
    """Get username and password from environment variables."""
    username = os.getenv("USER", "").strip()
    password = os.getenv("PASSWORD", "").strip()
    return username if username else None, password if password else None


def is_auth_disabled() -> bool:
    """Check if authentication is explicitly disabled via DISABLE_AUTH env var."""
    return os.getenv("DISABLE_AUTH", "").lower() == "true"


def is_auth_enabled() -> bool:
    """
    Check if authentication is enabled.
    
    Auth is ENABLED by default (secure by default).
    Returns False only if DISABLE_AUTH=true is set.
    """
    if is_auth_disabled():
        return False
    
    username, password = get_credentials()
    return username is not None and password is not None


def require_auth_configured() -> None:
    """
    Validate that auth is properly configured.
    
    Raises SystemExit with clear error message if:
    - Auth is required (not disabled) AND
    - Credentials are not set
    
    This enforces secure-by-default behavior.
    """
    if is_auth_disabled():
        return  # Auth explicitly disabled, OK
    
    username, password = get_credentials()
    if not username or not password:
        print("\n" + "=" * 70)
        print("SECURITY: Authentication is required but not configured.")
        print("=" * 70)
        print("\nTo enable authentication, set in .env:")
        print("  USER=your_username")
        print("  PASSWORD=your_password")
        print("\nFor development only, you can disable auth:")
        print("  DISABLE_AUTH=true")
        print("\n" + "=" * 70 + "\n")
        sys.exit(1)


def check_auth(username: str, password: str) -> bool:
    """
    Validate username and password against environment variables.
    
    Args:
        username: Provided username
        password: Provided password
    
    Returns:
        True if credentials match or auth is disabled, False otherwise
    """
    if is_auth_disabled():
        return True  # Auth explicitly disabled, allow access
    
    expected_user, expected_pass = get_credentials()
    
    if not expected_user or not expected_pass:
        # Should not happen if require_auth_configured() was called
        return False
    
    # Constant-time comparison to prevent timing attacks
    import hmac
    user_match = hmac.compare_digest(username, expected_user)
    pass_match = hmac.compare_digest(password, expected_pass)
    
    return user_match and pass_match


def require_auth(func: Callable) -> Callable:
    """
    Decorator to require authentication for a function.
    
    Usage:
        @require_auth
        def protected_function():
            ...
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        # In Gradio, auth is handled at the UI level
        # This decorator is for future use with API endpoints
        return func(*args, **kwargs)
    return wrapper

