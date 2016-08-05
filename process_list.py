"""
process_list.py can send the entire process list in a dict, with event_type: process_list (initially)
				and will ping the server when there's a change in the process list with a dict 
				of the additional or removed process(es), with event_type: process_update
"""

import psutil
from time import time, sleep
import json
import requests

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

def post_procs_list(procs, url):
	p_dicts = []
	for p in procs:
		try:
			p_dict = p.as_dict()
			p_dicts.append(p_dict)
		except:
			print("Process {} could not be rendered as dict".format(p))
			pass
	event = json.dumps({"event_type": "process_list", "procs": p_dicts})
	response = requests.post(url, data=json.dumps(event), headers={"Content-type": "application/json"})
	return response

if __name__ == "__main__":
	old_procs = list(psutil.process_iter())
	procs = old_procs[:]

	url = "http://0.0.0.0:8080/event_trigger"
	response = post_procs_list(procs, url)
	print("Posted procs list with response {}".format(response))

	# detect terminated and added processes, then update process list
	while True:
		terminated, alive = detect_terminate(procs)
		print("Terminated: {}".format(terminated))
		for p in terminated:
			p_dict = {}
			for q in old_procs:
				if q.pid == p.pid:
					try:
						p_dict = q.as_dict()
						print('Dict of terminated: {}'.format(p_dict))
					except:
						print('Cannot generated dict {}'.format(p))
						pass
			event = json.dumps({"event_type": "process_update", "update_type": "termination", "proc": p_dict, "pid": p.pid})
			response = requests.post(url, data=json.dumps(event), headers={"Content-type": "application/json"})
			print("Posted termination of process {} with response {}".format(p, response))
			procs.remove(p)
		added = detect_add(old_procs, procs)
		print("Added: {}".format(added))
		for p in added:
			p_dict = {}
			try:
				p_dict = p.as_dict()
				print('Dict of added: {}'.format(p_dict))
			except:
				print('Cannot generated dict {}'.format(p))
				pass		
			event = json.dumps({"event_type": "process_update", "update_type": "addition", "proc": p_dict, "pid": p.pid})
			response = requests.post(url, data=json.dumps(event), headers={"Content-type": "application/json"})
			print("Posted addition of process {} with response {}".format(p, response))
			procs.append(p)
		print("Size of procs list, old {}: new {}".format(len(old_procs), len(procs)))
		old_procs = procs[:]
		sleep(2.0 - time() % 2.0)
		procs = list(psutil.process_iter())


