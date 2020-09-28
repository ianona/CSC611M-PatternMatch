import pika,json,subprocess

connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='localhost'))

channel = connection.channel()

q=channel.queue_declare(queue='rpc_queue')
def fib(n):
    if n == 0:
        return 0
    elif n == 1:
        return 1
    else:
        return fib(n - 1) + fib(n - 2)


def on_request(ch, method, props, body):
    print(json.loads(body))
    body=json.loads(body)
    if str(body)=='Requesting Count':   
        print("COUNT")
        q=channel.queue_declare(queue='rpc_queue')
        print(q.method.consumer_count)
        # execute_command('curl -i -u guest:guest http://localhost:15672/api/queues/')
        ch.basic_publish(exchange='',
                     routing_key=props.reply_to,
                     properties=pika.BasicProperties(correlation_id = \
                                                         props.correlation_id),
                     body=str(q.method.consumer_count))
        ch.basic_ack(delivery_tag=method.delivery_tag)
        return

    n = int(body)

    print(" [.] fib(%s)" % n)
    response = fib(n)

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