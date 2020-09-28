import json 
import re
import time
import sys
import os
import csv
import datetime
import psutil
import pika
import uuid
import threading
from time import sleep

HOST='192.168.0.162'
PORT='5672'
credentials = pika.PlainCredentials('csc611m', 'btstans')

class RPCBroker(object):
    # Asynch
    internal_lock=threading.Lock()
    queue={}
    def __init__(self):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=HOST,port=PORT,virtual_host='/',credentials=credentials))

        self.channel = self.connection.channel()

        result = self.channel.queue_declare(queue='ll', exclusive=True)
        # self.channel.basic_qos(prefetch_count=1)
        self.queue_method = result.method
        self.callback_queue = result.method.queue

        self.count_id = None

        thread = threading.Thread(target=self._process_data_events)
        thread.setDaemon(True)
        thread.start()

        # self.channel.basic_consume(
        #     queue=self.callback_queue,
        #     on_message_callback=self.on_response,
        #     auto_ack=True)

    def _process_data_events(self):
        self.channel.basic_consume(
            queue=self.callback_queue,
            on_message_callback=self.on_response,
            auto_ack=True)

        while True:
            with self.internal_lock:
                self.connection.process_data_events()
                sleep(0.1)

    def on_response(self, ch, method, props, body):
        if props.correlation_id == self.count_id:
            self.count = int(body)
        else:
            self.queue[props.correlation_id] = body
        # if self.corr_id == props.correlation_id:
        #     self.response = body

    def call(self, n):
        corr_id = str(uuid.uuid4())
        if n[2]==None:
            self.count = None
            self.count_id = corr_id
        else:
            self.queue[corr_id] = None

        with self.internal_lock:
            self.channel.basic_publish(
                exchange='',
                routing_key='rpc_queue',
                properties=pika.BasicProperties(
                    reply_to=self.callback_queue,
                    correlation_id=corr_id,
                ),
                body=json.dumps(n))
        # self.response = None
        # self.corr_id = str(uuid.uuid4())
        # self.channel.basic_publish(
        #     exchange='',
        #     routing_key='rpc_queue',
        #     properties=pika.BasicProperties(
        #         reply_to=self.callback_queue,
        #         correlation_id=self.corr_id,
        #     ),
        #     body=json.dumps(n))
        # while self.response is None:
        #     self.connection.process_data_events()
        # return json.loads(self.response)

    # def callCount(self):
    #     corr_id = str(uuid.uuid4())
    #     self.count_id = corr_id
    #     with self.internal_lock:
    #         self.channel.basic_publish(
    #             exchange='',
    #             routing_key='rpc_queue',
    #             properties=pika.BasicProperties(
    #                 reply_to=self.callback_queue,
    #                 correlation_id=corr_id,
    #             ),
    #             body=json.dumps("RC"))
    #     print("Calling count")

    def isDone(self):
        empty = not all(self.queue.values())
        if not empty:
            return True

    def getResults(self):
        return self.queue.values()

    def isCountDone(self):
        return not self.count==None

    def getCount(self):
        return self.count


def fileCheck(fname):
    # load file
    f2 = open(fname, "r")
    sample = f2.read()
    f2.close()

    # Retrieve all the words in the sample text using regex
    regex = r"(?<![\w'])\w+?(?=\b)"
    words = re.findall(regex, sample)
    words = [word.lower() for word in words]

    kmp_rpc = RPCBroker()
    print(" [x] Requesting Count")
    kmp_rpc.call([dictionary,words,None])
    while not kmp_rpc.isCountDone():
        sleep(0.1)
    node_count = kmp_rpc.getCount()
    # node_count=2
    print("There are " + str(node_count) + " node/s available")

    # divide the words into n equal parts corresponding to the number of available nodes
    # this means that each node gets 1 load, round robin style
    RR = 1
    skip=int(len(words)/(node_count*RR))
    loads = []
    for i in range(0,node_count):
        if i==node_count-1:
            loads.append((i*skip,len(words)))
        else:
            loads.append((i*skip,(i+1)*skip))
    print(loads)

    count = 0
    start = time.time()
    for load in loads:
        count+=1
        print(" [x] Requesting Node " + str(count) + " to handle "+ str(load))
        kmp_rpc.call([dictionary,words,load])
        # errors.append(kmp_rpc.call([dictionary,words,load]))

    # print(" [x] Requesting Node 1 to handle "+ str(loads[0]))
    # kmp_rpc.call([dictionary,words,loads[0]])
    # # errors.append()
    # print(" [x] Requesting Node 2 to handle "+ str(loads[1]))
    # kmp_rpc.call([dictionary,words,loads[1]])
    # errors.append()
    
    print(" [x] Waiting to finish...")
    while not kmp_rpc.isDone():
        sleep(0.1)

    errors = kmp_rpc.getResults()
    errors = [json.loads(error) for error in errors]
    # print(errors)
    end = time.time()
    process = psutil.Process(os.getpid()) 
    memoryUse = process.memory_info().rss/1000000
    cpu=psutil.cpu_percent()
    ram=psutil.virtual_memory().percent
    return [len(words),sum(errors),(end-start),memoryUse,ram,cpu]

def writeResults(row):
    fname = 'kmp-ds.csv'
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
        print("Starting DS for KMP Algo on file: "+arg)
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
        print("Starting DS for KMP Algo on directory: "+arg)
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
