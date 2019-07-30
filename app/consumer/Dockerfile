FROM python:3-alpine

WORKDIR /app/

RUN pip install pika \
        --index-url http://mirrors.aliyun.com/pypi/simple/ \
        --trusted-host mirrors.aliyun.com

COPY consumer.py .

CMD ["python", "consumer.py"]