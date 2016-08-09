"""
process_list.py can send the entire process list in a dict, with event_type: process_list (initially)
				and will ping the server when there's a change in the process list with a dict 
				of the additional or removed process(es), with event_type: process_update
"""

import psutil
from time import time, sleep
import json
import requests

# with stored names
def get_procs_list():
	fetched_procs = list(psutil.process_iter())
	procs_id_name = {}
	procs = []
	for p in fetched_procs:
		procs.append(p)
		try:
			p_name = p.name()
		except:
			p_name = None
		procs_id_name[p.pid] = p_name
	return procs, procs_id_name

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
	old_procs, old_procs_id_name = get_procs_list()
	procs, procs_id_name = old_procs[:], old_procs_id_name

	url = "http://0.0.0.0:8080/event_trigger"
	response = post_procs_list(procs_id_name, url)
	print("Posted procs list with response {}".format(response))

	# detect terminated and added processes, then update process list
	while True:
		terminated, alive = detect_terminate(procs)
		print("Terminated: {}".format(terminated))
		for p in terminated:
			print("Terminated pid: {}".format(p.pid))
			if p.pid in old_procs_id_name:
				print("Matched with old pid")
				print("Name of terminated process: {}".format(old_procs_id_name[p.pid]))
			del procs_id_name[p.pid]
			# get the mode in data obj's names (vals) -- should give mode and all
			event = json.dumps({"event_type": "process_update", "update_type": "termination", "proc": procs_id_name, "pid": p.pid})
			response = requests.post(url, data=json.dumps(event), headers={"Content-type": "application/json"})
			print("Posted termination of process {} with response {}".format(p, response))
			procs.remove(p)
		added = detect_add(old_procs, procs)
		print("Added: {}".format(added))
		for p in added:
			try:
				p_name = p.name()
				print('Name of added: {}'.format(p_name))
				procs_id_name[p.pid] = p_name
			except:
				print('Cannot find name of {}'.format(p))
				pass		
			event = json.dumps({"event_type": "process_update", "update_type": "addition", "proc": procs_id_name, "pid": p.pid})
			response = requests.post(url, data=json.dumps(event), headers={"Content-type": "application/json"})
			print("Posted addition of process {} with response {}".format(p, response))
			procs.append(p)
		print("Size of procs list, old {}: new {}".format(len(old_procs), len(procs)))
		old_procs = procs[:]
		sleep(2.0 - time() % 2.0)
		procs, procs_id_name = get_procs_list()


