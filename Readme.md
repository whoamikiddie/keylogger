
# Python Keylogger

## Description
This project is designed for covert data collection on a target system. It gathers various types of information, encrypts it, and sends it via email. The collected data includes system information, browser history, screenshots, webcam images, microphone recordings, and clipboard contents. The script runs discreetly on both Windows and Linux systems.

## Features
- **Data Collection:**
  - System information (Windows/Linux)
  - Browser history
  - Screenshots
  - Webcam images
  - Microphone recordings
  - Clipboard contents (Windows only)
- **Encryption:** Data is encrypted using Fernet encryption before transmission.
- **Email Notification:** Encrypted data is sent via email to a specified address.

## Requirements
- Python 3.x
- Required Python packages 
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
   - Set the `email_address` and `password` variables in `send_mail()` function.
2. **Execution:**
   - Run the `keylogger.py` script. It will collect data for 5 minutes and send it via email.
3. **Customization:**
   - Modify regular expressions in `RegObject` class for file filtering.
   - Adjust paths (`export_path`, `screenshot_dir`, `webcam_dir`) for data storage and transmission.

## Notes
- This script is intended for educational purposes only.
- Use responsibly and ensure compliance with local laws and ethical guidelines.

## Disclaimer
The authors are not responsible for any misuse or damage caused by this software.

