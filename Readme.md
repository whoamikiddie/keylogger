# Python Keylogger

## Description
This project facilitates covert data collection on a target system. It gathers various types of information, encrypts them, and sends them via email. The collected data includes system information, browser history, screenshots, webcam images, microphone recordings, and clipboard contents. The script operates discreetly on both Windows and Linux systems.

## Features
- **Data Collection:**
  - Logging every keystroke and special characters
  - Gathering computer information (RAM, OS) and network information (IP address, MAC address)
  - Capturing clipboard contents (Windows only)
  - Taking screenshots periodically
  - Optionally recording microphone input (if implemented)

- **Encryption:** Data is securely encrypted using Fernet encryption before transmission.
- **Email Notification:** Encrypted data is sent via email to a specified address.

## Requirements
- Python 3.11.9
- Required Python packages:
  - `browserhistory`
  - `opencv-python`
  - `requests`
  - `sounddevice`
  - `cryptography`
  - `Pillow`
  - `pynput`
  - `win32clipboard` (Windows only)

## Usage
1. **Configuration:**
   - Set the `email_address` and `password` variables in the `send_mail()` function to specify the email address for sending data.
   
2. **Execution:**
   - Run the `keylogger.py` script. It will collect data for a specified duration (e.g., 5 minutes) and send it via email.

3. **Customization:**
   - Modify regular expressions in the `RegObject` class for custom file filtering based on your requirements.
   - Adjust paths (`export_path`, `screenshot_dir`, `webcam_dir`) to suit your preferred directories for data storage and transmission.

## Future Improvements
- **Telegram Bot Integration:** Extend the project to include Telegram bot functionality for sending collected data, such as screenshots and webcam images, securely via Telegram.
- **Executable Creation:** Develop a working executable with branding and logo for easier deployment.
- **File Encryption and Obfuscation:** Enhance security by implementing file encryption and obfuscation techniques to protect the log files.



## Notes
- This script is intended for educational purposes only. Ensure compliance with local laws and ethical guidelines before use.
- Use responsibly and avoid unauthorized use or deployment on systems without proper authorization.

## Disclaimer
The authors disclaim any responsibility for misuse or damage caused by the use of this software. Use at your own risk.



