"""
apps_foreground.py checks for the foreground (frontmost) app running, 
					and remembers the previous foreground (2nd frontmost)
					in case of closing (but not quitting) the frontmost
					TODO: detect closing (but not quitting) of an app for 
							the 2nd frontmost to be useful
"""

import applescript
import time

scpt = applescript.AppleScript('''
    on run
    	tell application "System Events"
            set activeApp to name of first application process whose frontmost is true
        end tell
        return activeApp
    end run
''')


# list of [curr_foreground, prev_foreground]
apps = [None, None]

while True:
	foreground = scpt.run()

	# if not the last app in foreground
	if apps[0] != foreground:
		apps[1] = apps[0]
		apps[0] = foreground
	print(foreground, apps)
	time.sleep(1)