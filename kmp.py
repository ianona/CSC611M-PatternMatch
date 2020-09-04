import json 
import re
import time
import sys
import os
import csv
import datetime

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

def fileCheck(fname):
    # load file
    f2 = open(fname, "r")
    sample = f2.read()
    f2.close()

    # Retrieve all the words in the sample text using regex
    regex = r"(?<![\w'])\w+?(?=\b)"
    words = re.findall(regex, sample)
    words = [word.lower() for word in words]
    errors=[]

    # Compare every word in sample to every word in dictionary via pattern match
    print("Mispelled words:")
    start = time.time()
    for word in words:
        found=False
        for d_word in dictionary:
            if not found and len(d_word) == len(word):
                found = KMPSearch(word, d_word) 

        # print out mispelled words
        if not found:
            errors.append(word)
            print(word)

    end = time.time()
    return [len(words),len(errors),(end-start)]

def writeResults(row):
    fname = 'kmp-seq-results.csv'
    if not os.path.exists(fname):
        f = open(fname, 'w')
        with f:
            writer = csv.writer(f)
            writer.writerow(['timestamp','file/folder name','total words','errors found','time elapsed'])

    with open(fname, 'a+', newline='') as write_obj:
        writer = csv.writer(write_obj)
        writer.writerow(row)


# This code is contributed by Bhavya Jain 


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

    timestamp = datetime.datetime.now()

    if os.path.isfile(arg):
        print("KMP Sequential Algorithm for file: "+arg)
        results = fileCheck(arg)
        timeElapsed = results[2]
        wordCount = results[0]
        errorCount = results[1]
        print("Execution time: " + str(timeElapsed))
        writeResults([timestamp,arg,wordCount,errorCount,timeElapsed])
    elif os.path.isdir(arg):
        print("KMP Sequential Algorithm for files in folder: "+arg)
        timeElapsed = 0
        wordCount=0
        errorCount=0
        for file in os.listdir(arg):
            print("FILENAME: " + file)
            results = fileCheck(arg+'/'+file)
            timeElapsed += results[2]
            wordCount+= results[0]
            errorCount+= results[1]
            print('-------------------')
        print("Execution time: " + str(timeElapsed))
        writeResults([timestamp,arg,wordCount,errorCount,timeElapsed])
    else:
        print("File/directory does not exist in project path")

  

