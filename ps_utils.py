import psutil

def check_process_running_by_file_name(proc_name, file_name):
	'''
	Check if there is any running process that contains the given name processName.
	'''
	#Iterate over the all the running process
	for proc in psutil.process_iter():
		try:
				# Check if process name contains the given name string.
				if proc_name.lower() in proc.name().lower() and proc.cmdline()[1].find(file_name):
						return True, proc.pid
		except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
				pass
	return False, None;
