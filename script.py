import os
import json
import time
import subprocess
import smtplib
from email.mime.text import MIMEText
from colorama import init, Fore, Style

init(autoreset=True)
os.system("chcp 65001")

def load_config():
    with open('config.json', 'r', encoding='utf-8') as file:
        return json.load(file)

def load_devices():
    devices = []
    invalid_lines = []
    with open('devices.txt', 'r', encoding='utf-8') as file:
        for line in file:
            line = line.strip()
            if not line:
                continue
            if '-' in line:
                ip, name = line.split('-', 1)
                devices.append((ip.strip(), name.strip()))
            else:
                invalid_lines.append(line)
                print(Fore.RED + f"Invalid line in devices.txt: {line}")
    return devices, invalid_lines

def ping_host(ip, name, attempts):
    successful_pings = 0
    print(Fore.BLUE + f"Starting ping for device: {name} ({ip})")
    for attempt in range(attempts):
        print(Fore.BLUE + f"[Ping {attempt + 1}/{attempts}] Pinging {ip} ({name})...")
        response = subprocess.run(
            ["ping", "-n", "1", ip],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding='utf-8'
        )
        if response.returncode == 0:
            print(Fore.GREEN + f"Ping {ip} ({name}): Response OK.")
            successful_pings += 1
        else:
            print(Fore.YELLOW + f"Ping {ip} ({name}): No response.")
        time.sleep(1)
    return successful_pings == attempts

def send_email(smtp_config, unavailable_hosts):
    if not unavailable_hosts:
        print(Fore.GREEN + "No hosts to report. Email will not be sent.")
        return

    body = "Unavailable hosts:\n" + "\n".join([f"{ip} {name}" for ip, name in unavailable_hosts])
    subject = "Unavailable Hosts Report"

    msg = MIMEText(body, "plain", "utf-8")
    msg['Subject'] = subject
    msg['From'] = smtp_config['sender_email']
    msg['To'] = smtp_config['receiver_email']

    try:
        with smtplib.SMTP(smtp_config['smtp_server'], smtp_config['port']) as server:
            server.starttls()
            server.login(smtp_config['sender_email'], smtp_config['password'])
            server.send_message(msg)
            print(Fore.GREEN + "Email sent successfully.")
    except Exception as e:
        print(Fore.RED + f"Error sending email: {e}")

def main():
    config = load_config()
    devices, invalid_lines = load_devices()
    smtp_config = config['email']
    attempts_per_check = config['ping']['attempts_per_check']
    check_retries = config['ping']['check_retries']
    time_between_checks = config['ping']['time_between_checks_seconds']
    send_on_single_fail = config['sendOnSingleFail']

    all_results = {device: [] for device in devices}

    for retry in range(check_retries):
        print("\n" + Fore.BLUE + f"--- Starting Check Round {retry + 1} of {check_retries} ---\n")
        for ip, name in devices:
            is_available = ping_host(ip, name, attempts_per_check)
            if is_available:
                print(Fore.LIGHTGREEN_EX + f"Host {ip} ({name}) is available.\n")
            else:
                print(Fore.RED + f"Host {ip} ({name}) is unavailable.\n")
            all_results[(ip, name)].append(is_available)
        
        if retry < check_retries - 1:
            print(Fore.YELLOW + f"Waiting {time_between_checks} seconds before retrying...\n")
            time.sleep(time_between_checks)
    
    unavailable_hosts = []
    for (ip, name), results in all_results.items():
        if not all(results):
            if send_on_single_fail or not any(results):
                unavailable_hosts.append((ip, name))

    if invalid_lines:
        print(Fore.RED + "Invalid entries in devices.txt:")
        for line in invalid_lines:
            print(Fore.RED + f"- {line}")
        unavailable_hosts.extend([("Invalid Line", line) for line in invalid_lines])

    send_email(smtp_config, unavailable_hosts)

if __name__ == "__main__":
    config = load_config()
    if not config['debugMode']:
        import ctypes
        ctypes.windll.user32.ShowWindow(ctypes.windll.kernel32.GetConsoleWindow(), 0)
    main()
