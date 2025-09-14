# Splash Turnstile Solver

This repository contains code developed as part of a technical challenge for a job screening process. The CAPTCHA-solving functionality was created to demonstrate technical skills in automation and problem-solving within a controlled, authorized environment.

This code is designed to solve any turnstile captcha where the challenge takes up the entire page such as:

<img width="1920" height="989" alt="Screenshot From 2025-09-14 14-41-31" src="https://github.com/user-attachments/assets/ff31bd3e-67b3-4dd2-af0f-6c5234b176bd" />

**Disclaimer: This code is provided for educational purposes only. Do not use without explicit authorization. The author is not responsible for any misuse or damage caused by this script**

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
