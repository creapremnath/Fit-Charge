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

# Import necessary modules
from passlib.context import CryptContext
from cryptography.fernet import Fernet
from config import settings

################################################################
key=settings.key

cipher_suite = Fernet(key)

# Initialize CryptContext
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def encrypt_password(password: str) -> str:
    """Encrypt a password using bcrypt."""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hashed password."""
    return pwd_context.verify(plain_password, hashed_password)

##################################################################
def data_encrypt(message):
    """Encrypt a message using Fernet."""
    return cipher_suite.encrypt(message).decode('utf-8')

def data_decrypt(encrypted_message):
    """Decrypt an encrypted message using Fernet."""
    return cipher_suite.decrypt(encrypted_message)

