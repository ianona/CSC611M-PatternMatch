import pika,json

host='192.168.0.162'
port='5672'

credentials = pika.PlainCredentials('csc611m', 'btstans')
connection = pika.BlockingConnection(pika.ConnectionParameters(host=host,port=port,credentials=credentials))
# connection = pika.BlockingConnection(
#     pika.ConnectionParameters(host='localhost'))
channel = connection.channel()

q=channel.queue_declare(queue='hello')
print(q.method.consumer_count)
channel.basic_publish(exchange='', routing_key='hello', body='Hello World!')
print(" [x] Sent 'Hello World!'")

channel.start_consuming()
connection.close()

# if __name__ == "__main__":    
    # # Loading dictionary
    # # Opening JSON file 
    # f = open('words_dictionary.json',) 

    # data = json.load(f) 
    # dictionary = []
    # for i in data:
    #     dictionary.append(i)
      
    # # Closing file 
    # f.close() 
    # words=["hello"]
    # channel.basic_publish(exchange='',
    #                   routing_key='hello',
    #                   body=json.dumps((dictionary,words,0,43)),
    #                   properties=pika.BasicProperties(
    #                       delivery_mode = 2, # make message persistent
    #                   ))
    # print(" [x] Sent Dictionary")

    # # get arguments
    # try:
    #     arg = sys.argv[1]
    # except:
    #     #fallback in case no argument was passed
    #     arg = "sample.txt"

    # if os.path.isfile(arg):
    #     timestamp = datetime.datetime.now()
    #     print("KMP Sequential Algorithm for file: "+arg)
    #     results = fileCheck(arg)
    #     timeElapsed = results[2]
    #     wordCount = results[0]
    #     errorCount = results[1]
    #     memory = results[3]
    #     ram = results[4]
    #     cpu = results[5]
    #     print("Execution time: " + str(timeElapsed))
    #     writeResults([timestamp,arg,wordCount,errorCount,timeElapsed,memory,ram,cpu])
    # elif os.path.isdir(arg):
    #     print("KMP Sequential Algorithm for files in folder: "+arg)
    #     for file in os.listdir(arg):
    #         timestamp = datetime.datetime.now()
    #         print("FILENAME: " + file)
    #         results = fileCheck(arg+'/'+file)
    #         timeElapsed = results[2]
    #         wordCount = results[0]
    #         errorCount = results[1]
    #         memory = results[3]
    #         ram = results[4]
    #         cpu = results[5]
    #         print("Execution time: " + str(timeElapsed))
    #         writeResults([timestamp,file,wordCount,errorCount,timeElapsed,memory,ram,cpu])
    #         print('-------------------')
    # else:
    #     print("File/directory does not exist in project path")




