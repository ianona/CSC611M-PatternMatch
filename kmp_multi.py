import threading
import time
import logging
import json 
import re
import sys
import os
import csv
import datetime
import multiprocessing as mp
import psutil

THREAD_COUNT = os.cpu_count()

logging.basicConfig(level=logging.DEBUG,
					format='(%(threadName)-10s) %(message)s',
					)

# Python program for KMP Algorithm 
def KMPSearch(pat, txt): 
	M = len(pat) 
	N = len(txt) 
  
	# create lps[] that will hold the longest prefix suffix  
	# values for pattern 
	lps = [0]*M 
	j = 0 # index for pat[] 
  
	# Preprocess the pattern (calculate lps[] array) 
	computeLPSArray(pat, M, lps) 
  
	i = 0 # index for txt[] 
	while i < N: 
		if pat[j] == txt[i]: 
			i += 1
			j += 1
  
		if j == M: 
			# print("Found pattern at index " + str(i-j))
			# print("MATCH: " + pat)
			j = lps[j-1] 
			return True
			# break
  
		# mismatch after j matches 
		elif i < N and pat[j] != txt[i]: 
			# Do not match lps[0..lps[j-1]] characters, 
			# they will match anyway 
			if j != 0: 
				j = lps[j-1] 
			else: 
				i += 1
	return False
  
def computeLPSArray(pat, M, lps): 
	len = 0 # length of the previous longest prefix suffix 
  
	lps[0] # lps[0] is always 0 
	i = 1
  
	# the loop calculates lps[i] for i = 1 to M-1 
	while i < M: 
		if pat[i]== pat[len]: 
			len += 1
			lps[i] = len
			i += 1
		else: 
			# This is tricky. Consider the example. 
			# AAACAAAA and i = 7. The idea is similar  
			# to search step. 
			if len != 0: 
				len = lps[len-1] 
  
				# Also, note that we do not increment i here 
			else: 
				lps[i] = 0
				i += 1


class workerProcess (mp.Process):
	def __init__(self, processID,startIndex,endIndex,words,errors,lock):
		super(workerProcess,self).__init__()
		self.processID=processID
		self.startIndex=startIndex
		self.endIndex=endIndex
		self.words=words
		self.lock = lock
		self.errors = errors

	def run(self):
		print("Starting " + self.name + " on words " + str(self.startIndex) + "-" + str(self.endIndex))
		for i in range(self.startIndex,self.endIndex):
			word=self.words[i]
			# for word in words:
			found=False
			for d_word in dictionary:
				if not found and len(d_word) == len(word):
					found = KMPSearch(word, d_word) 
				if found:
					break

			# print out misspelled words
			if not found:
				# logging.debug('Waiting for lock')
				# self.lock.acquire()
				# try:
				#   logging.debug('Acquired lock')
				#   global errors
				#   errors.append(word)
				# finally:
				#   logging.debug('Released Lock')
				#   self.lock.release()
				with self.lock:
					self.errors.value +=1
				print(word)

def fileCheck(fname):
	# load file
	f2 = open(fname, "r")
	sample = f2.read()
	f2.close()

	# Retrieve all the words in the sample text using regex
	regex = r"(?<![\w'])\w+?(?=\b)"
	words = re.findall(regex, sample)
	words = [word.lower() for word in words]

	skip=int(len(words)/THREAD_COUNT)
	ranges=[]
	for i in range(0,THREAD_COUNT):
		if i==THREAD_COUNT-1:
			ranges.append((i*skip,len(words)))
		else:
			ranges.append((i*skip,(i+1)*skip))

	processes=[]
	count=1
	errors = mp.Manager().Value('i',  0)
	lock = mp.Manager().Lock()

	for r in ranges:
		process = workerProcess(count, r[0],r[1],words,errors,lock)
		processes.append(process)
		count+=1

	print("Misspelled words:")
	start = time.time()
	[p.start() for p in processes]
	[p.join() for p in processes]
	end = time.time()
	process = psutil.Process(os.getpid()) 
	# in  bytes
	memoryUse = process.memory_info().rss
	cpu=psutil.cpu_percent()
	ram=psutil.virtual_memory().percent
	return [len(words),errors.value,(end-start),memoryUse,ram,cpu]

def writeResults(row):
	fname = 'kmp-parallel-multip-results.csv'
	if not os.path.exists(fname):
		f = open(fname, 'w')
		with f:
			writer = csv.writer(f)
			writer.writerow(['timestamp','file name','total words','errors found','time elapsed','memory','ram','cpu'])

	with open(fname, 'a+', newline='') as write_obj:
		writer = csv.writer(write_obj)
		writer.writerow(row)

if __name__ == "__main__":
	# Loading dictionary
	# Opening JSON file 
	f = open('words_dictionary.json',) 

	data = json.load(f) 
	dictionary = []
	for i in data:
		dictionary.append(i)
	  
	# Closing file 
	f.close() 
	# get arguments
	try:
		arg = sys.argv[1]
	except:
		#fallback in case no argument was passed
		arg = "sample.txt"

	if os.path.isfile(arg):
		timestamp = datetime.datetime.now()
		print("KMP Parallel Multiprocessing Algorithm for file: "+arg)
		results = fileCheck(arg)
		timeElapsed = results[2]
		wordCount = results[0]
		errorCount = results[1]
		memory = results[3]
		ram = results[4]
		cpu = results[5]
		print("Execution time: " + str(timeElapsed))
		writeResults([timestamp,arg,wordCount,errorCount,timeElapsed,memory,ram,cpu])
	elif os.path.isdir(arg):
		print("KMP Parallel Multiprocessing Algorithm for files in folder: "+arg)
		for file in os.listdir(arg):
			timestamp = datetime.datetime.now()
			print("FILENAME: " + file)
			results = fileCheck(arg+'/'+file)
			timeElapsed = results[2]
			wordCount = results[0]
			errorCount = results[1]
			memory = results[3]
			ram = results[4]
			cpu = results[5]
			print("Execution time: " + str(timeElapsed))
			writeResults([timestamp,file,wordCount,errorCount,timeElapsed,memory,ram,cpu])
			print('-------------------')
	else:
		print("File/directory does not exist in project path")

	print ("Exiting Main Thread") 

