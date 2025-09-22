import subprocess
from subprocess import DEVNULL
import argparse
import time
import json
import requests
import sys
import websocket
from websocket import create_connection

def connect_to_page(port):
	"""
	Connect to a Chrome DevTools Protocol debugging session for a Cloudflare challenge page.
	
	Searches for a browser tab with the title "Just a moment..." (typically a Cloudflare 
	challenge page) and establishes a WebSocket connection to its CDP endpoint.
	
	Args:
		port (int): The local port number where Chrome's debugging interface is running
	
	Returns:
		WebSocket connection object if successful, None if connection fails or page not found
	
	Raises:
		requests.exceptions.ConnectionError: If unable to connect to the debugging interface
	"""

	dBugUrl = f'http://127.0.0.1:{port}/json'
	try:
		rsp = requests.get(dBugUrl).json()
		for i in range(len(rsp)):
			if rsp[i]['title'] == 'Just a moment...':
				return create_connection(rsp[i]['webSocketDebuggerUrl'])
	except requests.exceptions.ConnectionError:
		return

def send_CDP_command(websocket, command, params={}):
	"""
	Send a Chrome DevTools Protocol command through an established WebSocket connection.
	
	Formats and sends a CDP command with parameters to the browser instance. Each command
	is assigned a unique request ID for response tracking.
	
	Args:
		websocket: Active WebSocket connection to CDP endpoint
		command (str): CDP method name (e.g., 'Runtime.evaluate', 'Network.getAllCookies')
		params (dict, optional): Command parameters. Defaults to empty dict.
	
	Note:
		Increments global requestID counter for command tracking
	"""

	global requestID
	requestID += 1
	websocket.send(json.dumps({'method': command,
			'id': requestID,
			'params': params}))

def get_CDP_response(websocket):
	"""
	Retrieve and parse the CDP response matching the last sent command.
	
	Continuously reads WebSocket messages until finding a response with the matching
	request ID from the most recently sent command.
	
	Args:
		websocket: Active WebSocket connection to CDP endpoint
	
	Returns:
		dict: Parsed JSON response from the CDP command
	"""

	while True:
		rsp = json.loads(websocket.recv())
		if rsp['id'] == requestID:
			return rsp

def parse_for_cf_clearance(websocket):
	"""
	Extract the Cloudflare clearance cookie from the current browser session.
	
	Retrieves all cookies from the active page and searches for the 'cf_clearance'
	cookie, which indicates successful completion of Cloudflare's challenge.
	
	Args:
		websocket: Active WebSocket connection to CDP endpoint
	
	Returns:
		dict: Cookie object containing cf_clearance data if found, None otherwise
	
	Note:
		The cf_clearance cookie is set by Cloudflare after successful challenge completion
	"""

	send_CDP_command(websocket, 'Network.getAllCookies')
	cookies = get_CDP_response(websocket)['result']['cookies']
	for i in cookies:
		if i['name'] == 'cf_clearance':
			return i

def check_title(websocket):
	"""
	Check if current page is still showing the Cloudflare challenge.
	
	Evaluates JavaScript to get the page title and determines if the Cloudflare
	challenge page ("Just a moment...") is active.
	
	Args:
		websocket: Active WebSocket connection to CDP endpoint
	
	Returns:
		bool: True if page title is "Just a moment...", False otherwise
	"""

	send_CDP_command(websocket, 'Runtime.evaluate', {"expression":"document.querySelector('head > title').innerHTML"})
	value=get_CDP_response(websocket)
	if value != None and value['result']['result']['type'] == 'string':
		if value['result']['result']['value'] == 'Just a moment...':
			return True
		else:
			return False

def click_turnstile(websocket):
	"""
	Attempt to solve Cloudflare's Turnstile challenge through automated interaction.
	
	Performs a series of keyboard and mouse interactions to trigger the Turnstile
	verification process.
	
	Args:
		websocket: Active WebSocket connection to CDP endpoint
	
	Returns:
		bool: True if challenge appears to be solved (title changes from "Just a moment..."),
		False if all attempts fail
	  
	Note:
		- Makes up to 3 attempts with 30 interaction cycles each
		- Includes delays between actions
		- Success is determined by checking if the page title changes
	"""

	for i in range(3):
		for i in range(30):
			send_CDP_command(websocket, "Input.dispatchKeyEvent", {"type":"keyDown","key":"Tab"})
			time.sleep(0.1)
			send_CDP_command(websocket, "Input.dispatchKeyEvent", {"type":"keyDown","code":"Space","key":" "})
			send_CDP_command(websocket, "Input.dispatchKeyEvent", {"type":"keyUp","code":"Space","key":" "})
			time.sleep(0.1)
			send_CDP_command(websocket, "Input.dispatchMouseEvent", {"type":"mousePressed","x":100,"y":100,"button":"left"})
			time.sleep(0.1)
			if check_title(websocket) == True:
				time.sleep(0.1)
				continue
			else:
				return True
		time.sleep(5)
	return False


#Initialize CDP request ID
requestID = 0

def main():

	#Chromium debugging port
	dBugPort = 3000

	#Parse arguments
	parser = argparse.ArgumentParser(description="splash-screen style CAPTCHA solver")
	parser.add_argument('url', type=str, help='Target URL')
	parser.add_argument('--proxy', '-p', default='', help='Optional proxy server')
	args = parser.parse_args()

	#Launch chromium session with sand-boxed data directory, incognito, proxy, and debugging enabled
	proc = subprocess.Popen(
		['chromium', '--user-data-dir=/tmp/chrometmp', '--incognito', f'--remote-debugging-port={dBugPort}',
		f'--remote-allow-origins=http://127.0.0.1:{dBugPort}', f'--proxy-server={args.proxy}', args.url],
		stderr=DEVNULL)

	#Connect to page via CDP web-socket
	for i in range(5):
		ws = connect_to_page(dBugPort)
		if isinstance(ws, websocket._core.WebSocket):
			break
		else:
			time.sleep(0.2)
	if not isinstance(ws, websocket._core.WebSocket):
		print("Failed to connect to splash style CAPTCHA page")
		exit(1)
	print("Connected to target page")

	time.sleep(1)

	#Bypass turnstile captcha
	results = click_turnstile(ws)
	if results == True:
		print('Bypass successful')
	elif results == False:
		print('Bypass failed')
		exit(1)

	#Grab cf_clearance cookie
	cf_clearance = parse_for_cf_clearance(ws)

	#Kill browser process
	proc.kill()

	#Print value of cf_clearance if found
	if cf_clearance != None:
		print('cf_clearance = '+cf_clearance['value'])
	else:
		print("No cf_clearance cookie recovered")

if __name__ == '__main__':
	main()