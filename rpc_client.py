import pika
import uuid
import json

class FibonacciRpcClient(object):

    def __init__(self):
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(host='localhost'))

        self.channel = self.connection.channel()

        result = self.channel.queue_declare(queue='ll', exclusive=True)
        # self.channel.basic_qos(prefetch_count=1)
        self.queue_method = result.method
        self.callback_queue = result.method.queue

        self.channel.basic_consume(
            queue=self.callback_queue,
            on_message_callback=self.on_response,
            auto_ack=True)

    def on_response(self, ch, method, props, body):
        if self.corr_id == props.correlation_id:
            self.response = body

    def call(self, n):
        self.response = None
        self.corr_id = str(uuid.uuid4())
        self.channel.basic_publish(
            exchange='',
            routing_key='rpc_queue',
            properties=pika.BasicProperties(
                reply_to=self.callback_queue,
                correlation_id=self.corr_id,
            ),
            body=json.dumps(n))
        while self.response is None:
            self.connection.process_data_events()
        return int(self.response)

    def getCount(self):
        print(self.channel.consumer_tags)
        self.response = None
        self.corr_id = str(uuid.uuid4())
        self.channel.basic_publish(
            exchange='',
            routing_key='rpc_queue',
            properties=pika.BasicProperties(
                reply_to=self.callback_queue,
                correlation_id=self.corr_id,
            ),
            body=json.dumps("Requesting Count"))
        while self.response is None:
            self.connection.process_data_events()
        return int(self.response)


fibonacci_rpc = FibonacciRpcClient()
c=fibonacci_rpc.getCount()
print(c)
print(" [x] Requesting 3 fib")
response = fibonacci_rpc.call(30)
response2 = fibonacci_rpc.call(21)
response3 = fibonacci_rpc.call(25)
print(" [.] Got %r" % response)
print(" [.] Got %r" % response2)
print(" [.] Got %r" % response3)