# turnstile-captcha-solver
Bypass splash screen turnstile CAPTCHA, built as a coding challenge

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
