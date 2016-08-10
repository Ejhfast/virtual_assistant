"""
process_list.py can send the entire process list in a dict, with event_type: process_list (initially)
				and will ping the server when there's a change in the process list with a dict 
				of the additional or removed process(es), with event_type: process_update
"""

import json
import requests
import subprocess, shlex
import csv
import psutil

def get_applications():
	file_path = "applications.csv"
	file = open(file_path, "wb")
	subprocess.call(shlex.split("find '/Applications' -maxdepth 1 -iname '*.app'"), stdout=file)
	apps = []
	with open(file_path, "rb") as file:
		for row in file:
			app_name = str(row).split('/')[2].split('.app')[0]
			print(app_name)
			apps.append(app_name)
	return apps

def is_running(procs_names):
	procs_status = {}
	fetched_procs = []
	for p in list(psutil.process_iter()):
		try:
			name = p.name()
		except:
			name = False
		fetched_procs.append(name)
	for name in procs_names:
		if name is False or name not in fetched_procs:
			procs_status[name] = False
		else:
			procs_status[name] = True
	return procs_status

def post_procs_list(procs_status, url, event_type):
	event = json.dumps({"event_type": event_type, "procs": procs_status})
	response = requests.post(url, data=json.dumps(event), headers={"Content-type": "application/json"})
	return response

if __name__ == "__main__":
	apps = get_applications()
	procs_status = is_running(apps)
	url = "http://0.0.0.0:8080/event_trigger"
	event_type = "process_list"
	response = post_procs_list(procs_status, url, event_type)
	print(procs_status, response)
