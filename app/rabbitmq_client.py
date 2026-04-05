import json
import pika


def send_message(data):
    print("SEND_MESSAGE CALLED")

    try:
        print("Trying RabbitMQ connection...")

        credentials = pika.PlainCredentials("guest", "guest")

        parameters = pika.ConnectionParameters(
            host="localhost",
            port=5672,
            credentials=credentials,
            blocked_connection_timeout=3,
            socket_timeout=3
        )

        connection = pika.BlockingConnection(parameters)
        print("Connected to RabbitMQ")

        channel = connection.channel()

        channel.queue_declare(queue="ticket_queue", durable=True)
        channel.queue_declare(queue="ticket_log_queue", durable=True)

        message = json.dumps(data)

        channel.basic_publish(
            exchange="",
            routing_key="ticket_queue",
            body=message,
            properties=pika.BasicProperties(delivery_mode=2)
        )

        channel.basic_publish(
            exchange="",
            routing_key="ticket_log_queue",
            body=message,
            properties=pika.BasicProperties(delivery_mode=2)
        )

        print("Message sent to RabbitMQ and ticket_log_queue")

        connection.close()

    except Exception as e:
        print("RabbitMQ ERROR:", e)