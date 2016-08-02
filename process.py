import psutil

pids = psutil.pids()
zombie_count = 0
zombies = []
for pid in pids:
	p = psutil.Process(pid)
	try:
		# if p.name() == 'Preview':
		# 	p.terminate()
		print(pid, p.name(), p.environ())
	except:
		print('Zombie Process with pid {}'.format(pid))
		zombie_count += 1
		zombies.append(pid)
		pass
print(zombie_count, zombies)
for pid in zombies:
	p = psutil.Process(pid)
	print(p)