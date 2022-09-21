import psutil

def check_process_running_by_file_name(proc_name, file_name, ignore_pid):
	'''
	Check if there is any running process that contains the given name processName.
	'''
	#Iterate over the all the running process
	for proc in psutil.process_iter():
		try:
				# Check if process name contains the given name string and isn't the process calling this.
				if proc_name.lower() in proc.name().lower() and proc.cmdline()[1].find(file_name) == 0 and proc.pid != ignore_pid:
						return True, proc.pid
		except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
				print("Exception in check_process_running_by_file_name")
				pass
	return False, None;
