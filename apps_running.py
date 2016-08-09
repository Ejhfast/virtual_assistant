"""
process_list.py can send the entire process list in a dict, with event_type: process_list (initially)
				and will ping the server when there's a change in the process list with a dict 
				of the additional or removed process(es), with event_type: process_update
"""

from time import time, sleep
import json
import requests
import subprocess
import csv

def get_applications():
	file_path = "applications.csv"
	# process = subprocess.Popen(("find /Applications -maxdepth 1 -iname *.app > " + file_path).split(), stdout=subprocess.PIPE)
	process = subprocess.Popen("find ~/Applications* -maxdepth 1 -iname *.app".split(), stdout=subprocess.PIPE)
	output = process.communicate()[0]
	print(output)
	apps = []
	for x in output:
		apps.append(str(x)[14:-4])
		print(apps)
	# apps_path_len = len("/Applications/")
	# ext_len = len(".app")
	# apps = []
	# with open(file_path, 'rb') as file:
	# 	reader = csv.reader(file)
	# 	for row in reader:
	# 		apps.append(row[apps_path_len : -ext_len - 1])
	return apps

def is_running(procs_names):
	procs_status = []
	for name in procs_names:
		

def on_terminate(proc):
	print("Process {} terminated with exit code {}".format(proc, proc.returncode))

def detect_terminate(procs):
	terminated, alive = psutil.wait_procs(procs, timeout=2, callback=on_terminate)
	return terminated, alive

def detect_add(procs, new_procs):
	added = []
	for p in new_procs:
		if p not in procs:
			added.append(p)
	return added

def post_procs_list(procs, url, event_type):
	data = {}
	for p in procs:
		try:
			p_name = p.name()
			data[p.pid] = p_name
		except:
			print("Process {} had no name".format(p))
			pass
	event = json.dumps({"event_type": "process_list", "procs": data})
	response = requests.post(url, data=json.dumps(event), headers={"Content-type": "application/json"})
	return response

if __name__ == "__main__":
	apps = get_applications()
	print(apps)

