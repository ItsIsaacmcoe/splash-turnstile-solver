import subprocess
from subprocess import DEVNULL
import time
import json
import requests
import sys
import websocket
from websocket import create_connection

#Return web-socket connection for page with title Just a moment...
def connect_to_page(port):
	dBugUrl = f'http://127.0.0.1:{port}/json'
	try:
		rsp = requests.get(dBugUrl).json()
		for i in range(len(rsp)):
			if rsp[i]['title'] == 'Just a moment...':
				return create_connection(rsp[i]['webSocketDebuggerUrl'])
	except requests.exceptions.ConnectionError:
		return False

#Send formatted command to CDP server
def send_CDP_command(websocket, command, params={}):
	global requestID
	requestID += 1
	websocket.send(json.dumps({'method': command,
			'id': requestID,
			'params': params}))

#Return current CDP response
def get_CDP_response(websocket):
	while True:
		rsp = json.loads(websocket.recv())
		if rsp['id'] == requestID:
			return rsp

#Search active page for cf_clearance cookie
def parse_for_cf_clearance(websocket):
	send_CDP_command(websocket, 'Network.getAllCookies')
	cookies = get_CDP_response(websocket)['result']['cookies']
	for i in cookies:
		if i['name'] == 'cf_clearance':
			return i

#Test page title for "Just a moment" with CDP
def check_title(websocket):
	send_CDP_command(websocket, 'Runtime.evaluate', {"expression":"document.querySelector('head > title').innerHTML"})
	value=get_CDP_response(websocket)
	if value != None and value['result']['result']['type'] == 'string':
		if value['result']['result']['value'] == 'Just a moment...':
			return True
		else:
			return False

#Click turnstile and check results
def click_turnstile(websocket):
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

	#Set site url and optional proxy server
	if len(sys.argv) == 1:
		print("url required")
		exit(1)
	elif len(sys.argv) == 2:
		proxyServer=''
	elif len(sys.argv) >= 3:
		proxyServer = sys.argv[2]
	target_url = sys.argv[1]

	#Launch chromium session with sand-boxed data directory, incognito, proxy, and debugging enabled
	proc = subprocess.Popen(
		['chromium', '--user-data-dir=/tmp/chrometmp', '--incognito', f'--remote-debugging-port={dBugPort}',
		f'--remote-allow-origins=http://127.0.0.1:{dBugPort}', f'--proxy-server={proxyServer}', target_url],
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
