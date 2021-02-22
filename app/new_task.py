import os
import pika
import sys

host, port = os.environ["RABBITMQ_ADDR"].split(":")
connection = pika.BlockingConnection(
    pika.ConnectionParameters(
        host=host,
        port=port
    )
)
channel = connection.channel()

channel.queue_declare(queue='task_queue', durable=True)

message = ' '.join(sys.argv[1:]) or "Hello World!"
channel.basic_publish(
    exchange='',
    routing_key='task_queue',
    body=message,
    properties=pika.BasicProperties(
        delivery_mode=2,  # make message persistent
    ))
print(" [x] Sent %r" % message)
connection.close()
