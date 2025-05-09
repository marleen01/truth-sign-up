# Truth Sign-Up

A Python project to automate account creation on the Truth Social Android app using ADB, with support for multiple devices and threaded workflows.

## Features

* **ADB Automation**: Controls the Truth Social app via Android Debug Bridge.
* **Multi-Device Support**: Run concurrent sign-up threads across multiple connected devices or emulators.
* **Randomized Data Generation**: Generates realistic user data (names, emails, phone numbers) for each account.
* **Proxy Management**: Route traffic through HTTP or SOCKS proxies listed in `proxy.txt`.
* **Email and SMS Verification**: Fetch verification codes automatically.
* **Error Recovery**: Retries on failures and logs detailed diagnostics.

## Prerequisites

* **Python 3.8+**
* **ADB** installed and accessible in your `PATH`
* **Truth Social** Android APK installed on your device/emulator
* One or more Android devices or emulators connected and authorized for ADB

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/marleen01/truth-sign-up.git
   cd truth-sign-up
   ```
2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

## Configuration

1. Rename `config.txt` to `.env` and fill in the following values:

   ```ini
   ADB_PATH=/path/to/adb
   APP_NAME=com.truth.android
   ```
2. Update `proxy.txt` with one proxy per line (e.g., `http://user:pass@host:port`).
3. (Optional) Populate `forenames.txt` and `surnames.txt` with custom name lists.

## Usage

Run the main script with optional arguments:

```bash
python main.py \
  --devices 2 \
  --threads 4 \
  --timeout 30
```

### Common Options

* `--devices`: Number of devices/emulators to use (default: 1)
* `--threads`: Number of concurrent sign-up threads per device (default: 2)
* `--timeout`: Seconds to wait for UI element responses (default: 20)

## Project Structure

```
├── adb/                 # Utility for ADB commands
├── config.py            # Loads environment configuration
├── generate_data.py     # Random user data generators
├── proxy_manager.py     # Proxy loading and rotation
├── get_mail.py          # Email verification helper
├── get_phone.py         # SMS verification helper
├── ui_automation.py     # UI interaction logic
├── recovery.py          # Error handling and retry logic
├── main.py              # Entry point
├── proxy.txt            # Proxy list
├── forenames.txt        # First name list
├── surnames.txt         # Last name list
├── requirements.txt     # Python dependencies
└── LICENSE              # CC0 1.0 Universal
```

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for bug fixes and enhancements.

## License

This project is released under the **CC0 1.0 Universal** license. See [LICENSE](LICENSE) for details.
