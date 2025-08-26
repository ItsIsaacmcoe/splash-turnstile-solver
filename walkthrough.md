## Launch Chromium
An instance of Chromium browser is opened at the target url with remote debugging set to allow interaction over the Chrome Devtools Protocol (CDP). It also uses a unique data directory so as not to interfere with other browser sessions and incognito mode to ensure output cookies are unique upon each execution.
## Connect to open page containing CAPTCHA
To find the websocket address associated with the page containing the target CAPTCHA, the script queries the http endpoint at `http://127.0.0.1:{dBugPort}/json` and searches the pages for the title `Just a moment...` extracting the value of `webSocketDebuggerUrl`.

It then connects using `create_connection` from Python Websocket. This creates an object connected to the target page that can send and receive CDP commands.

This task is attempted several times a second by the function `connect_to_CDP()` until success, thus enabling the script to continue the moment a connection is made.

The script will exit if this process fails.
## Attempt CAPTCHA bypass
After resting for half a second to let the page start to load, the script calls `click_turnstile()` a function that uses CDP to issue these commands several times a second for a couple seconds:
- Tab
- Space
- Mouseclick in empty space
- Test if the page title is still `Just a moment...`

Then pauses for 5 seconds (to handle cases where extra challenge Javascript is executed) and tries again up to three times.

If the page title changes at any point during this process, the function returns True and passes control back to `main()`
## Recovering cf_clearance cookie
The CDP function `Network.getAllCookies` is used to grab all browser cookies. The response is parsed as a list for the value of `name`. If that value is `cf_clearance` it is printed.
## Challenges
#### Turnstile checkbox in closed shadow DOM
Checkbox inaccessible via Javascript. If accessible, its availability could be checked directly and in a more timely fashion. Could be clicked on using `.click` instead of issuing direct inputs.
#### Javascript execution triggered by checkbox is well obfuscated.
I believe this event can be found and the script could avoid checking the box altogether. Time constraints forced my focus towards the method I present.
