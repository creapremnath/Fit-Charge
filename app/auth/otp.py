"""
Private License (Fit-Charge)

This script is privately licensed and confidential. It is not intended for
public distribution or use without explicit permission from the owner.

All rights reserved (c) 2024.
"""

__author__ = "Premnath Palanichamy"
__copyright__ = "Copyright 2024, Fit-Charge"
__license__ = "Refer Terms and Conditions"
__version__ = "1.0"
__maintainer__ = "Premnath"
__email__ = "creativepremnath@gmail.com"
__status__ = "Development"
__desc__ = "OTP function Fit-Charge applications"


#Import
import random
import time

otp_store = {}

def generate_otp(email):
    if email in otp_store:
        del otp_store[email]

    # Generate OTP (6-digit number)
    otp = random.randint(100000, 999999)
    print(f"Generated OTP for {email}: {otp}")

    # Store the OTP with expiration time (e.g., 5 minutes from now)
    expiration_time = time.time() + 105  # 300 seconds = 5 minutes
    otp_store[email] = {"otp": otp, "expiration_time": expiration_time}

    # Print the updated otp_store for debugging
    print(f"Updated otp_store: {otp_store}")

    # Return the generated OTP
    return otp

def verify_otp(email, otp):
    # Get the OTP data for the given email
    otp_data = otp_store.get(email)
    if not otp_data:
        return f"No OTP generated for {email}."

    # Check if OTP has expired
    current_time = time.time()
    if current_time > otp_data["expiration_time"]:
        del otp_store[email]  # Remove expired OTP
        return f"OTP for {email} has expired."

    # Print debug information
    print(f"Attempting to verify OTP for {email}. OTP provided: {otp}")
    print(f"Stored OTP for verification: {otp_data['otp']}")

    # Verify OTP
    is_valid = otp_data["otp"] == otp
    if is_valid:
        # Successfully verified OTP
        print(otp_store, "before delete")
        del otp_store[email]
        print(otp_store, "after delete")
        return True
    else:
        # Invalid OTP
        print(otp_store, "On error")
        return f"Invalid OTP for {email}."
