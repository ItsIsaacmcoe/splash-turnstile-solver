# Splash Turnstile Solver

This repository contains code designed to solve Cloudflare splash-screen turnstile CAPTCHA and was created to demonstrate technical skills in automation within a controlled and authorized environment.

_Disclaimer: This code is provided for educational purposes only. Do not use without explicit authorization. The author is not responsible for any misuse or damage caused by this script_

## "Splash-Style CAPTCHA"

This code prints a cf_clearance cookie for any site containing Cloudflare CAPTCHA where the challenge takes up the entire page such as:

<img width="1920" height="989" alt="Screenshot From 2025-09-14 14-41-31" src="https://github.com/user-attachments/assets/ff31bd3e-67b3-4dd2-af0f-6c5234b176bd" />

## Requirements

- Python 3.x
- Chromium browser installed and accessible via the command line as `chromium`
- Python packages:
	- `requests`
	- `websocket-client`

## Usage

Run script from the command line:
`python scriptname.py {options} <url>`
- `<url>`: The target URL to load in Chromium (required)
# Script Execution
##### Chromium Launches

An instance of Chromium browser is opened with remote debugging set to allow interaction over the Chrome Devtools Protocol (CDP). It also uses a unique data directory so as not to interfere with other browser sessions.
##### CAPTCHA Page Confirmation

The web-socket address associated with the page containing CAPTCHA is found by querying the HTTP endpoint at `http://127.0.0.1:{dBugPort}/json`. This return Json that contains web-socket addresses for all open tabs. The data is parsed for the open page with the title `Just a moment...`, it's associated address is used to create a web-socket object connected to the target page that can send and receive CDP commands.
##### Bypass Attempt

After resting a second to let the page load, `click_turnstile()` uses CDP to issue these commands several times a second for a couple seconds:
- Tab
- Space
- Mouse-click in empty space
- Test if the page title is still `Just a moment...`

Then pauses for 5 seconds (to handle cases where extra challenge JavaScript is executed) and tries again up to three times.

If the page title changes at any point during this process, the function returns True and passes control back to `main()`
##### Recovering `cf_clearance` Cookie

The CDP function `Network.getAllCookies` is used to grab all browser cookies. The response is parsed as a list for the value of `name`. If that value is `cf_clearance` it is printed.

