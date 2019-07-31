# rabbitmq-ha-demo
A project for demostrating a rabbitmq cluster.

## Mirroring

rabbitmqctl set_policy ha-all "^" '{"ha-mode":"all"}'

## References
[pardahlman/docker-rabbitmq-cluster](https://github.com/pardahlman/docker-rabbitmq-cluster)