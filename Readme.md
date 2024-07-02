Python Keylogger

Overview

This Python script serves as a keylogger designed to capture keystrokes, take screenshots, record microphone input, and capture webcam images on both Windows and Linux platforms. It encrypts sensitive data and sends it via email using SMTP.
Features

    Keylogging: Captures keystrokes and logs them into a file (key_logs.txt).
    Encryption: Encrypts sensitive files using the Fernet encryption scheme.
    Data Capture:
        Screenshots every 5 seconds for 5 minutes.
        Records microphone input for 1 minute.
        Captures webcam images every 5 seconds for 5 minutes.
        Retrieves system information (Windows and Linux).
        Gathers browser history.
        Retrieves clipboard contents (Windows).
        Retrieves network information.

Usage
Prerequisites

    Python 3.x installed.
    Required Python packages installed (pip install -r requirements.txt).

Configuration

    Email Setup:
        Replace email_address and password variables in send_mail() function with your email credentials.

    Encryption Key:
        Ensure the key variable in encrypt_data() function (key = b'T2UnFbwxfVlnJ1PWbixcDSxJtpGToMKotsjR4wsSJpM=') is securely stored and managed.

Running the Script

    Execute python keylogger.py in the terminal.
    The script will run processes to capture data for 5 minutes, encrypt it, and send it via email.

Decryption (Not Included in Script)

    Decryption Functionality: Not implemented in the provided script. Modify the script to include decryption using Fernet.decrypt() with the encryption key (key) securely managed.

Important Notes

    Security: Handle sensitive data responsibly and comply with legal regulations.
    Email: Ensure proper email configuration and consider security implications.
    Logging: Monitor logs (key_logs.txt) for captured keystrokes and data.

Disclaimer

This script is intended for educational purposes only. The use of this script without appropriate authorization may be against the law in your jurisdiction. The author and OpenAI do not condone illegal activities or malicious use of this script. Use it responsibly and at your own risk.