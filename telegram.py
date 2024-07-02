import os
import time
import json
import requests
from collections import defaultdict
from daemon import DaemonContext

# Load the token and chat ID from the configuration file
with open('config.json', 'r') as f:
    config = json.load(f)
    telegram_token = config['telegram_token']
    telegram_chat_id = config['telegram_chat_id']

# Dictionary to store last modified times of files
last_modified_times = defaultdict(int)

def send_to_telegram(bot_token, chat_id, directory):
    url_document = f'https://api.telegram.org/bot{bot_token}/sendDocument'
    files_to_send = []

    for root, _, files in os.walk(directory):
        for file_name in files:
            file_path = os.path.join(root, file_name)
            try:
                current_time = os.path.getmtime(file_path)
                last_modified_time = last_modified_times[file_path]

                if current_time != last_modified_time:
                    files_to_send.append(file_path)
                    last_modified_times[file_path] = current_time
                else:
                    print(f"File {file_path} has not been updated since last check.")
            except FileNotFoundError:
                print(f"File {file_path} not found")
            except Exception as e:
                print(f"Error processing {file_path}: {e}")

    # Send all collected files in a batch
    if files_to_send:
        send_files_batch(files_to_send, url_document, chat_id)

def send_files_batch(files_to_send, url, chat_id):
    try:
        files = {}
        for file_path in files_to_send:
            with open(file_path, 'rb') as f:
                file_name = os.path.basename(file_path)
                files[file_name] = (file_name, f)

        params = {'chat_id': chat_id}
        response = requests.post(url, files=files, params=params)
        response.raise_for_status()
        print(f"{len(files_to_send)} files sent successfully to Telegram")
    except Exception as e:
        print(f"Error sending files to Telegram: {e}")

def send_message(message, chat_id):
    send_message_url = f'https://api.telegram.org/bot{telegram_token}/sendMessage'
    params = {'chat_id': chat_id, 'text': message}
    response = requests.post(send_message_url, params=params)
    response.raise_for_status()
    print(f"Message sent: {message}")

def main():
    directory_to_monitor = '/tmp/logs' if os.name != 'nt' else 'C:\\tmp'

    # Initial check and sending of files
    send_to_telegram(telegram_token, telegram_chat_id, directory_to_monitor)

    # Periodic check every 5 minutes
    while True:
        print("Checking files for updates...")
        send_to_telegram(telegram_token, telegram_chat_id, directory_to_monitor)
        time.sleep(300)

if __name__ == "__main__":
    with DaemonContext():
        main()
