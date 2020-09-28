import pika, sys, os,json

def main():
    host='192.168.0.162'
    port='5672'
    credentials = pika.PlainCredentials('csc611m', 'btstans')
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=host,port=port,virtual_host='/',credentials=credentials))
    channel = connection.channel()

    channel.queue_declare(queue='hello')

    def callback(ch, method, properties, body):
        # print(type(body))
        # if type(body)=='bytes':
        #     body=json.loads(body)
        # dic=body[0]
        # words=body[1]
        # start=body[2]
        # end=body[3]
        # print(start)
        # print(end)
        print(" [x] Received %r" % body)
        channel.basic_publish(exchange='', routing_key='result', body='Hello from recipient')

    channel.basic_consume(queue='hello', on_message_callback=callback, auto_ack=True)

    print(' [*] Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)