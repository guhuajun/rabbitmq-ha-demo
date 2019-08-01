# -*- coding: utf-8 -*-
# pylint: disable=


import os
import random
import logging
import time
import uuid
from datetime import datetime

import pika
from retry import retry


if __name__ == "__main__":
    # change logging config
    logging.basicConfig(level=logging.INFO,
                        format='[%(asctime)s.%(msecs)03d][%(filename)s:%(lineno)d][%(levelname)s]%(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')

    logger = logging.getLogger(__file__)

    try:
        producer_delay = float(os.getenv('PRODUCER_DELAY', 1.0))
    except:
        producer_delay = 1.0
    logger.info('Producer delay: %s', producer_delay)

    @retry(pika.exceptions.AMQPConnectionError, delay=10, jitter=(1, 3))
    def produce():
        connection = None
        while not connection:
            try:
                parameters = pika.URLParameters('amqp://guest:guest@haproxy:5672/%2F')
                connection = pika.BlockingConnection(parameters)
            except:
                logger.error(
                    'Failed to establish connection to cluster')
                time.sleep(10)

        channel = connection.channel()
        channel.queue_declare(queue='test', arguments={'x-ha-policy': 'all'})

        counter = 0
        while True:
            try:

                connection.sleep(producer_delay)
                body = '{0}:{1}'.format(
                    datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f') ,str(uuid.uuid4()))
                channel.basic_publish(exchange='',
                                      routing_key='test',
                                      body=body)
                counter += 1
                if counter % 500 == 0:
                    logger.info('Sent %s messages.', str(counter))
            except Exception as ex:
                logger.error(str(ex))
                time.sleep(1)

        connection.close()

    produce()
