#!/bin/bash

set -e

rabbitmq-server -detached
rabbitmqctl stop_app
rabbitmqctl reset