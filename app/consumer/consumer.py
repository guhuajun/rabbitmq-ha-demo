# -*- coding: utf-8 -*-
# pylint: disable=

# Ref: https://pika.readthedocs.io/en/stable/examples/blocking_consume_recover_multiple_hosts.html

import re
import random
import os
import logging
import time
from datetime import datetime

import pika
from retry import retry


if __name__ == "__main__":
    # change logging config
    logging.basicConfig(level=logging.INFO,
                        format='[%(asctime)s.%(msecs)03d][%(filename)s:%(lineno)d][%(levelname)s]%(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')

    logger = logging.getLogger(__file__)

    # Assuming there are two hosts: rabbitmq2, and rabbitmq3
    node2 = pika.URLParameters('amqp://172.24.0.11')
    node3 = pika.URLParameters('amqp://172.24.0.12')
    all_endpoints = [node2, node3]

    def on_message(ch, method, properties, body):
        seq_num = int(re.findall('\d+', str(body))[0])
        if seq_num % 500 == 0:
            logger.info('Consumed %s', str(body))

        # insert a randon delay when acking messages
        # https://stackoverflow.com/questions/22061082/getting-pika-exceptions-connectionclosed-error-while-using-rabbitmq-in-python
        # delay_seconds = random.randint(1, 3) * 0.1
        # connection.sleep(delay_seconds)

        ch.basic_ack(delivery_tag=method.delivery_tag)

    @retry(pika.exceptions.AMQPConnectionError, delay=10, jitter=(1, 3))
    def consume():
        random.shuffle(all_endpoints)
        connection = pika.BlockingConnection(all_endpoints)
        channel = connection.channel()
        channel.basic_qos(prefetch_count=1)

        # This queue is intentionally non-durable. See http://www.rabbitmq.com/ha.html#non-mirrored-queue-behavior-on-node-failure
        # to learn more.
        channel.queue_declare('test')
        channel.basic_consume('test', on_message)

        try:
            channel.start_consuming()
        except KeyboardInterrupt:
            channel.stop_consuming()
            connection.close()
        except pika.exceptions.ConnectionClosedByBroker:
            # Uncomment this to make the example not attempt recovery
            # from server-initiated connection closure, including
            # when the node is stopped cleanly
            # except pika.exceptions.ConnectionClosedByBroker:
            #     pass
            pass

    consume()
