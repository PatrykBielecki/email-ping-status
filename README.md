# Email Ping Status Checker

This tool monitors device availability using ping and sends an email alert if devices are unreachable.

## Configuration

### `config.json`

- **Email Settings**:
  - `smtp_server`: SMTP server (e.g., `smtp.gmail.com`).
  - `port`: SMTP port (e.g., `587` for TLS).
  - `sender_email`: Sender's email address.
  - `password`: Sender's email password.
  - `receiver_email`: Recipient's email address.
- **Ping Settings**:
  - `attempts_per_check`: Number of ping attempts per device.
  - `check_retries`: Number of retry rounds.
  - `time_between_checks_seconds`: Time (in seconds) between retries.
- **Behavior**:
  - `sendOnSingleFail`: `true` to send email on the first failure.
  - `debugMode`: `true` to show logs and wait for user input, `false` to run silently.

Example:

```json
{
    "email": {
        "smtp_server": "smtp.example.com",
        "port": 587,
        "sender_email": "youremail@example.com",
        "password": "yourpassword",
        "receiver_email": "receiver@example.com"
    },
    "ping": {
        "attempts_per_check": 3,
        "check_retries": 2,
        "time_between_checks_seconds": 10
    },
    "sendOnSingleFail": true,
    "debugMode": false
}
```

### `devices.txt`

List devices in the following format:

```txt
192.168.1.1 - Router
192.168.1.2 - Desktop
10.0.0.5 - Server
```

Place config.json and devices.txt in the same folder as the script or executable.
