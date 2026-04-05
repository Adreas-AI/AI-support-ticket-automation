import json
import pika


def callback(ch, method, properties, body):
    data = json.loads(body)
    print("Received message:", data)

    # εδώ μετά μπορούμε να βάλουμε πραγματική δουλειά
    # π.χ. notification (ειδοποίηση), logging (καταγραφή), CRM sync (συγχρονισμός)

    ch.basic_ack(delivery_tag=method.delivery_tag)


connection = pika.BlockingConnection(
    pika.ConnectionParameters(host="localhost")
)
channel = connection.channel()

channel.queue_declare(queue="ticket_queue", durable=True)

channel.basic_consume(
    queue="ticket_queue",
    on_message_callback=callback
)

print("Worker is waiting for messages...")
channel.start_consuming()