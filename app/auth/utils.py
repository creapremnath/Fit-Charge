"""
Private License (qtools)

This script is privately licensed and confidential. It is not intended for
public distribution or use without explicit permission from the owner.

All rights reserved (c) 2024.
"""

__author__ = "Premnath Palanichamy"
__copyright__ = "Copyright 2024, qtools"
__license__ = "Refer Terms and Conditions"
__version__ = "1.0"
__maintainer__ = "Premnath"
__email__ = "creativepremnath@gmail.com"
__status__ = "Development"
__desc__ = "Main Program of qtools applications"

from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, VerificationError
from cryptography.fernet import Fernet
from app.core.config import settings
from app.core.database import get_session
from sqlmodel import Session
from app.api.v1.user.models import User
import getpass
import re

# -----------------------------------------------------------
# Utilities
# -----------------------------------------------------------

key = settings.key
cipher_suite = Fernet(key)
ph = PasswordHasher()

def encrypt_password(password: str) -> str:
    return ph.hash(password)


# -----------------------------------------------------------
# Colors for CLI
# -----------------------------------------------------------
RED = "\033[91m"
GREEN = "\033[92m"
CYAN = "\033[96m"
YELLOW = "\033[93m"
RESET = "\033[0m"


# -----------------------------------------------------------
# Email validation
# -----------------------------------------------------------
def is_valid_email(email: str) -> bool:
    pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    return re.match(pattern, email) is not None


# -----------------------------------------------------------
# Main function
# -----------------------------------------------------------
def superadmincreation():
    """Create a super admin user from the command line."""
    
    print(f"{CYAN}Superuser creation utility{RESET}")

    try:
        session = next(get_session())
    except Exception as e:
        print(f"{RED}Error: Unable to initialize database session.{RESET}")
        print(f"{YELLOW}Details: {e}{RESET}")
        return

    try:
        # --------------------------
        # Email Input
        # --------------------------
        email = input("Email: ").strip()
        if not email:
            print(f"{RED}Error: Email is required.{RESET}")
            return
        
        if not is_valid_email(email):
            print(f"{RED}Error: Invalid email format.{RESET}")
            return

        # Check if exists
        if session.query(User).filter(User.email == email).first():
            print(f"{RED}Error: A user with this email already exists.{RESET}")
            return

        # --------------------------
        # Username Input
        # --------------------------
        username = input("Username: ").strip()
        if not username:
            print(f"{RED}Error: Username is required.{RESET}")
            return

        # --------------------------
        # Password Input
        # --------------------------
        while True:
            password = getpass.getpass("Password: ")
            password2 = getpass.getpass("Password (again): ")

            if password != password2:
                print(f"{RED}Error: Passwords do not match.{RESET}")
                continue

            if len(password) < 8:
                print(f"{RED}Error: Password must be at least 8 characters.{RESET}")
                continue

            break

        # --------------------------
        # Create User Object
        # --------------------------
        user_obj = User(
            username=username,
            email=email,
            password=encrypt_password(password),
            is_active=True,
            is_verified=True,
            role=0,  # superadmin
        )

        session.add(user_obj)

        try:
            session.commit()
            print(
                f"{GREEN}Superuser created successfully!{RESET} "
                f"[username: {username}, email: {email}]"
            )
        except Exception as e:
            session.rollback()
            print(f"{RED}Error: Failed to create user due to a database error.{RESET}")
            print(f"{YELLOW}Details: {e}{RESET}")

    except Exception as e:
        print(f"{RED}Unexpected error during superuser creation.{RESET}")
        print(f"{YELLOW}Details: {e}{RESET}")

    finally:
        session.close()
