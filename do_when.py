from datetime import datetime
from threading import Timer
import logging
import sqlite3
import os
import sys
import ps_utils

###################################################
# Functions
###################################################

###################################################
def leap_year(y):
	if y % 400 == 0:
		return True
	if y % 100 == 0:
		return False
	if y % 4 == 0:
		return True
	else:
		return False

###################################################
def increment_year(date):

	new_date = date.replace(year=date.year+1)

	logging.debug("new_date in increment_month: "+str(new_date))
	return new_date

###################################################
def increment_month(date):

	if date.month == 12:
		new_date = date.replace(year=date.year+1, month=1)
	else:
		new_date = date.replace(month=date.month+1)

	logging.debug("new_date in increment_month: "+str(new_date))
	return new_date
		
###################################################
def increment_day(date):
	
	if leap_year(date.year) and date.month == 2:
		if date.day == 29:
			new_date = date.replace(month=3, day=1)
		else:
			new_date = date.replace(day=date.day+1)
	elif (date.month == 2 and date.day == 28) or (date.month in [1,3,5,7,8,10,12] and date.day == 31) or (date.month in [4,6,9,11] and date.day == 30):
		temp_date = date.replace(day=1)
		new_date = increment_month(temp_date)
	else:
		new_date = date.replace(day=date.day+1)

	logging.debug("new_date in increment_month: "+str(new_date))
	return new_date

###################################################
def increment_hour(date):
	if date.hour == 23:
		temp_date = increment_day(date)
		new_date = temp_date.replace(hour=0)
	else:
		new_date = date.replace(hour=date.hour+1)

	logging.debug("new_date in increment_month: "+str(new_date))
	return new_date

###################################################
def do_work(work_item):
	logging.debug("Working on: "+ work_item[1] + " at " + str(datetime.now()))
	os.system(work_item[1])

	db_conn = None

	try:
		db_conn = sqlite3.connect("stuff_to_do")
	except Error as e:
		loggin.Error("Failed to connect to DB: "+e)
		sys.exit()

	curr = db_conn.cursor()

	x=datetime.strptime(work_item[2], '%Y-%m-%d %H:%M:%S.%f')
	next_do_time = None

	if work_item[3] == "yearly":
		next_do_time = increment_year(x)
	elif work_item[3] == "hourly":
		x = datetime.today()
		# Since an hour is pretty short don't want the timing to be absolute.
		next_do_time = increment_hour(x) 
	elif work_item[3] == "daily":
		next_do_time = increment_day(x)
	elif work_item[3] == "weekly":
		next_do_time = x
		for i in range (1,8):
			next_do_time = increment_day(next_do_time)
	elif work_item[3] == "monthly":
		next_do_time = increment_month(x)
	elif work_item[3] == "hourly-weekdays":
		logging.info("hourly-weekdays is not yet supported")
	elif work_item[3] == "daily-weekdays":
		wk_day_num = datetime.now().isoweekday()
		next_do_time = x
		if wk_day_num <= 4:
			next_do_time = increment_day(next_do_time)
		else:
			while wk_day_num <=7:
				wk_day_num += 1
				next_do_time = increment_day(next_do_time)


	last_done_time = datetime.today()

	curr.execute("INSERT or REPLACE into stuff_to_do VALUES("+str(work_item[0])+",'"+work_item[1]+"','"+str(next_do_time)+"','"+work_item[3]+"','"+ str(last_done_time)+"')")
	db_conn.commit()
	db_conn.close()

###################################################
def fetch_all_todos():
	db_conn = None

	try:
		db_conn = sqlite3.connect("stuff_to_do")
	except Error as e:
		logging.error("Failed to connect to DB: "+e)
		sys.exit()

	cur = db_conn.cursor()
	cur.execute("SELECT * FROM stuff_to_do")
	rows = cur.fetchall()
	db_conn.close()

	return rows

###################################################
def main_loop():

	logging.info("main_loop at "+str(datetime.today()))
		
	rows = fetch_all_todos()

	logging.debug(rows)

	for item in rows:

		try:
			next_go_date = datetime.strptime(item[2], '%Y-%m-%d %H:%M:%S.%f')
			if next_go_date < datetime.today():
				do_work(item)
		except:
			logging.debug("Item "+str(item[0])+" did not have a good date: "+item[2])

	t = Timer(180, main_loop)
	t.start()


###################################################
def delete_todo(inst):
	logging.info("deleting todo instance "+str(inst))

	db_conn = None

	try:
		db_conn = sqlite3.connect("stuff_to_do")
		cur = db_conn.cursor()
		cur.execute("delete FROM stuff_to_do where id="+ str(inst))
		db_conn.commit()
		cur.close()
	except Error as e:
		logging.error("Failed to connect to DB: "+e)
		sys.exit()

###################################################
def list_todos():
		
	rows = fetch_all_todos()

	for item in rows:
		print(item)

###################################################
def print_cli_help():
	print("\t -k: Kill the currently running do_when")
	print("\t -s: Start do_when")
	print("\t -d <id>: Delete a to do")
	print("\t -l: list all to_dos")
	print("\t -r: run raw")


###################################################
# MAIN
###################################################

logging.basicConfig(level=logging.INFO, format='%(message)s')

# Handle script args #############################
for i in range(sys.argv.__len__()):
	if i == 0:
		continue
	if sys.argv[i] == "-l":
		list_todos()
		sys.exit()
	elif sys.argv[i] == '-k':
		is_running, proc_num = ps_utils.check_process_running_by_file_name("Python", os.path.abspath(__file__), os.getpid())
		if is_running == True:
			kill_str = "kill -15 "+str(proc_num)
			os.system(kill_str)
			print("Killed proc num "+str(proc_num))
		else:
			print("Not running")
		sys.exit()
	elif sys.argv[i] == '-d':
		i += 1
		try:
			if int(sys.argv[i]) >= 0:
				delete_todo(sys.argv[i])
		except:
			print("Failed to convert id argument to number. Did you include one?")
		sys.exit()
	elif sys.argv[i] == '-s':
		is_running, proc_num = ps_utils.check_process_running_by_file_name("Python", os.path.abspath(__file__), os.getpid())
		if is_running == False:
			os.system("rm "+os.path.abspath(".")+"/nohup.out")
			os.system("nohup /usr/bin/python3 "+ os.path.abspath(__file__) + "&")
			is_running, proc_num = ps_utils.check_process_running_by_file_name("Python", os.path.abspath(__file__), os.getpid())
			print(os.path.abspath(__file__))
			if is_running == False:
				print("Did not start!")
			else:
				print("Started as proc num: "+str(proc_num))
		else:
			print("Already running as proc num "+str(proc_num))
		sys.exit()
	elif sys.argv[i] == '-r':
		is_running, proc_num = ps_utils.check_process_running_by_file_name("Python", os.path.abspath(__file__), os.getpid())
		if is_running == True:
			kill_str = "kill -15 "+str(proc_num)
			os.system(kill_str)
			print("Killed proc num "+str(proc_num))
		main_loop()
		sys.exit()
	elif sys.argv[i] == "-h" or sys.argv[i] != "-r" or sys.argv[i] != "-s" or sys.argv[i] != "-k" or sys.argv[i] != "-d" or sys.argv[i] != "-l":
		print_cli_help()
		sys.exit()
# Handle script args #############################


is_running, proc_num = ps_utils.check_process_running_by_file_name("Python", os.path.abspath(__file__), os.getpid())
if is_running == True:
	print("Already running as proc num "+str(proc_num))
else:
	main_loop()
