# splash-turnstile-solver

This repository contains code developed as part of a technical challenge for a job screening process. The CAPTCHA-solving functionality was created to demonstrate technical skills in automation and problem-solving within a controlled, authorized environment.

*Disclaimer: This code is provided for educational purposes only. The author is not responsible for any misuse or damage caused by this script*

## Requirements

- Python 3.x
- Chromium browser installed and accessible via the command line as `chromium`
- Python packages:
	- `requests`
	- `websocket-client`

## Usage

Run script from the command line:
`python scriptname.py <url> [proxy]`
- `<url>`: The target URL to load in Chromium (required)
- `[proxy]`: Optional proxy server string (e.g., `http://127.0.0.1:8080`)