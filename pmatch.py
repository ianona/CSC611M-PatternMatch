import json 
import re
import time
  
# Loading dictionary
# Opening JSON file 
f = open('words_dictionary.json',) 

data = json.load(f) 
dictionary = []
for i in data:
	dictionary.append(i)
  
# Closing file 
f.close() 

# Loading sample text
f2 = open("sample.txt", "r")
sample = f2.read()
f2.close()

# Retrieve all the words in the sample text using regex
regex = r"(?<![\w'])\w+?(?=\b)"
words = re.findall(regex, sample)

# naive search algorithm
def search(pat, txt): 
    M = len(pat) 
    N = len(txt) 
  
    # A loop to slide pat[] one by one */ 
    for i in range(N - M + 1): 
        j = 0
          
        # For current index i, check  
        # for pattern match */ 
        while(j < M): 
            if (txt[i + j] != pat[j]): 
                break
            j += 1
  
        if (j == M and len(pat)==len(txt)):  
        	# print(pat + " is a word: " + txt)
        	break
            # print("Pattern found at index ", i) 
  
# Turn dictionary array into one string
dict_string = ' '.join([str(elem) for elem in dictionary]) 

# Compare every word in sample to every word in dictionary via pattern match
start = time.time()
for word in words:
	for d_word in dictionary:
		search(word,d_word)
end = time.time()
print("Execution time: " + str(end - start))






