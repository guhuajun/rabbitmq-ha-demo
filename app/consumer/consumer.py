# -*- coding: utf-8 -*-
# pylint: disable=


import re
import random
import os
import logging
import time
from datetime import datetime

import pika


if __name__ == "__main__":
    # change logging config
    logging.basicConfig(level=logging.INFO,
                        format='[%(asctime)s.%(msecs)03d][%(filename)s:%(lineno)d][%(levelname)s]%(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')

    logger = logging.getLogger(__file__)

    amqp_broker_host = os.getenv('AMQP_BROKER_HOST', 'haproxy')
    amqp_broker_port = os.getenv('AMQP_BROKER_PORT', '5672')

    connection = None
    while not connection:
        try:
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(amqp_broker_host, amqp_broker_port))
        except:
            logger.error('Lost connection to %s', amqp_broker_host)
            time.sleep(5)

    channel = connection.channel()
    channel.queue_declare(queue='test')

    def callback(ch, method, properties, body):
        seq_num = int(re.findall('\d+', str(body))[0])
        if seq_num % 100 == 0:
            logger.info('Consumed %s', str(body))

        # insert a randon delay when acking messages
        # https://stackoverflow.com/questions/22061082/getting-pika-exceptions-connectionclosed-error-while-using-rabbitmq-in-python
        # delay_seconds = random.randint(1, 3) * 0.1
        # connection.sleep(delay_seconds)

        ch.basic_ack(delivery_tag = method.delivery_tag)

    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(
        queue='test', on_message_callback=callback)

    logger.info('Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()
