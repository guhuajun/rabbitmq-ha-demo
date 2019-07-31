# -*- coding: utf-8 -*-
# pylint: disable=


import os
import random
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
            time.sleep(10)

    channel = connection.channel()
    channel.queue_declare(queue='test', arguments={'x-ha-policy':'all'})

    counter = 0
    while True:
        try:
            channel.basic_publish(exchange='',
                                  routing_key='test',
                                  body='Message {0}'.format(str(counter)))
            counter += 1
            if counter % 1000 == 0:
                logger.info('Sent %s messages.', str(counter))
        except Exception as ex:
            logger.error(str(ex))
        finally:
            delay_sec = random.randint(1, 9) * 0.01
            connection.sleep(delay_sec)

    connection.close()
