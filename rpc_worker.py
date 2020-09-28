import pika,json,subprocess

HOST='192.168.0.162'
PORT='5672'
credentials = pika.PlainCredentials('csc611m', 'btstans')

connection = pika.BlockingConnection(pika.ConnectionParameters(host=HOST,port=PORT,virtual_host='/',credentials=credentials))

channel = connection.channel()

q=channel.queue_declare(queue='rpc_queue')

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

def on_request(ch, method, props, body):
    # print(json.loads(body))
    body=json.loads(body)
    dictionary = body[0]
    words = body[1]
    load = body[2]

    # if broker is requesting count, send total node count
    if load == None:   
        print(" [x] Node Count Requested")
        q=channel.queue_declare(queue='rpc_queue')
        # print(q.method.consumer_count)
        # execute_command('curl -i -u guest:guest http://localhost:15672/api/queues/')
        ch.basic_publish(exchange='',
                     routing_key=props.reply_to,
                     properties=pika.BasicProperties(correlation_id = \
                                                         props.correlation_id),
                     body=str(q.method.consumer_count))
        ch.basic_ack(delivery_tag=method.delivery_tag)
        return

    # print(" [.] fib(%s)" % n)
    # response = fib(n)
    # response="LOL"
    
    start = load[0]
    end = load[1]
    errors = 0

    print(" [x] Processing words " + str(start) + "-" + str(end))

    for i in range(start,end):
            word=words[i]
            # for word in words:
            found=False
            for d_word in dictionary:
                if not found and len(d_word) == len(word):
                    found = KMPSearch(word, d_word) 
                if found:
                    break

            # print out mispelled words
            if not found:
                errors += 1
                print(word)

    response = errors

    ch.basic_publish(exchange='',
                     routing_key=props.reply_to,
                     properties=pika.BasicProperties(correlation_id = \
                                                         props.correlation_id),
                     body=str(response))
    ch.basic_ack(delivery_tag=method.delivery_tag)

channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue='rpc_queue', on_message_callback=on_request)

print(" [x] Awaiting RPC requests")
channel.start_consuming()