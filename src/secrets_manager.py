"""Secure secrets management using system keyring."""

import getpass
import os
from pathlib import Path
from typing import Optional, List, Dict

# Suppress noisy keyring warnings before importing
import warnings
warnings.filterwarnings("ignore", message=".*keyring.*")
warnings.filterwarnings("ignore", category=UserWarning)

try:
    import keyring
    from keyring.backends import fail
    KEYRING_AVAILABLE = True
    
    # Try to use encrypted file backend if no system backend is available
    try:
        backend = keyring.get_keyring()
        backend_name = type(backend).__name__.lower()
        
        # If using plaintext backend, switch to encrypted
        if 'plaintext' in backend_name:
            try:
                from keyrings.alt.file import EncryptedKeyring
                enc_keyring = EncryptedKeyring()
                # Set file location in project data directory
                data_dir = Path(__file__).parent.parent / "data"
                enc_keyring.file_path = str(data_dir / ".keyring_encrypted")
                keyring.set_keyring(enc_keyring)
            except Exception:
                pass  # Keep using plaintext if encrypted fails
    except Exception:
        pass
        
except ImportError:
    KEYRING_AVAILABLE = False

# Service name for keyring storage
SERVICE_NAME = "jobhelper"

# Known secret keys and their descriptions
SECRET_KEYS = {
    "OPENAI_API_KEY": "OpenAI API key for AI-powered job scraping",
    "SMTP_HOST": "SMTP server hostname (e.g., smtp.gmail.com)",
    "SMTP_PORT": "SMTP server port (e.g., 587)",
    "SMTP_USER": "SMTP username/email",
    "SMTP_PASSWORD": "SMTP password or app-specific password",
    "NOTIFY_EMAIL": "Email address to receive job notifications",
}


def is_keyring_available() -> bool:
    """Check if keyring is available and functional."""
    if not KEYRING_AVAILABLE:
        return False
    
    try:
        # Test that keyring backend is working
        backend = keyring.get_keyring()
        # Check if it's the fail backend (no real backend available)
        if isinstance(backend, fail.Keyring):
            return False
        # Also check for chainer with no viable backends
        backend_name = type(backend).__name__.lower()
        if 'fail' in backend_name:
            return False
        return True
    except Exception:
        return False


def get_secret(key: str, silent: bool = False) -> Optional[str]:
    """
    Retrieve a secret from the keyring.
    
    Args:
        key: The secret key name (e.g., 'OPENAI_API_KEY')
        silent: If True, suppress error messages
        
    Returns:
        The secret value, or None if not found
    """
    if not is_keyring_available():
        return None
    
    try:
        return keyring.get_password(SERVICE_NAME, key)
    except Exception as e:
        if not silent:
            print(f"Warning: Could not retrieve secret '{key}': {e}")
        return None


def set_secret(key: str, value: str) -> bool:
    """
    Store a secret in the keyring.
    
    Args:
        key: The secret key name
        value: The secret value
        
    Returns:
        True if successful, False otherwise
    """
    if not is_keyring_available():
        print("Error: Keyring is not available on this system.")
        return False
    
    try:
        keyring.set_password(SERVICE_NAME, key, value)
        return True
    except Exception as e:
        print(f"Error storing secret '{key}': {e}")
        return False


def delete_secret(key: str) -> bool:
    """
    Delete a secret from the keyring.
    
    Args:
        key: The secret key name
        
    Returns:
        True if successful, False otherwise
    """
    if not is_keyring_available():
        print("Error: Keyring is not available on this system.")
        return False
    
    try:
        keyring.delete_password(SERVICE_NAME, key)
        return True
    except keyring.errors.PasswordDeleteError:
        # Secret doesn't exist, that's fine
        return True
    except Exception as e:
        print(f"Error deleting secret '{key}': {e}")
        return False


def list_secrets() -> Dict[str, bool]:
    """
    List all known secret keys and whether they're configured.
    
    Returns:
        Dictionary mapping key names to configured status
    """
    result = {}
    
    for key in SECRET_KEYS:
        value = get_secret(key, silent=True)
        result[key] = value is not None and len(value) > 0
    
    return result


def interactive_set_secret(key: str) -> bool:
    """
    Interactively prompt for and set a secret.
    
    Args:
        key: The secret key name
        
    Returns:
        True if successful, False otherwise
    """
    if key not in SECRET_KEYS:
        print(f"Warning: '{key}' is not a recognized secret key.")
        print(f"Known keys: {', '.join(SECRET_KEYS.keys())}")
        confirm = input("Set it anyway? (y/n): ").strip().lower()
        if confirm != 'y':
            return False
    else:
        print(f"\n{key}: {SECRET_KEYS[key]}")
    
    # Check current value
    current = get_secret(key)
    if current:
        print(f"Current value: {'*' * min(len(current), 8)}{'...' if len(current) > 8 else ''}")
        confirm = input("Overwrite? (y/n): ").strip().lower()
        if confirm != 'y':
            print("Cancelled.")
            return False
    
    # Prompt for new value (hidden input for sensitive keys)
    sensitive_keys = ["API_KEY", "PASSWORD", "SECRET", "TOKEN"]
    is_sensitive = any(s in key.upper() for s in sensitive_keys)
    
    if is_sensitive:
        value = getpass.getpass(f"Enter value for {key}: ")
    else:
        value = input(f"Enter value for {key}: ").strip()
    
    if not value:
        print("No value entered. Cancelled.")
        return False
    
    if set_secret(key, value):
        print(f"✓ Secret '{key}' stored securely in system keyring.")
        return True
    
    return False


def print_secrets_status():
    """Print the status of all known secrets."""
    print("\n=== Secrets Status ===\n")
    
    if not is_keyring_available():
        print("⚠ Keyring is not available on this system.")
        print("  Falling back to .env file for configuration.")
        print("  Install keyring support: pip install keyring\n")
        return
    
    secrets = list_secrets()
    
    for key, description in SECRET_KEYS.items():
        configured = secrets.get(key, False)
        status = "✓ configured" if configured else "✗ not set"
        print(f"  {key}")
        print(f"    {description}")
        print(f"    Status: {status}\n")


# CLI interface for testing
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print_secrets_status()
        sys.exit(0)
    
    command = sys.argv[1]
    
    if command == "list":
        print_secrets_status()
    
    elif command == "set" and len(sys.argv) >= 3:
        key = sys.argv[2]
        interactive_set_secret(key)
    
    elif command == "get" and len(sys.argv) >= 3:
        key = sys.argv[2]
        value = get_secret(key)
        if value:
            print(f"{key}: {'*' * 8}... (hidden)")
        else:
            print(f"{key}: not set")
    
    elif command == "delete" and len(sys.argv) >= 3:
        key = sys.argv[2]
        if delete_secret(key):
            print(f"✓ Secret '{key}' deleted.")
        else:
            print(f"✗ Could not delete '{key}'.")
    
    else:
        print("Usage:")
        print("  python secrets_manager.py list")
        print("  python secrets_manager.py set <KEY>")
        print("  python secrets_manager.py get <KEY>")
        print("  python secrets_manager.py delete <KEY>")
