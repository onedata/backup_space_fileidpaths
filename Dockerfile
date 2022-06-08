FROM python:3.10.5-alpine3.16

MAINTAINER Bartek Kryza <bkryza@gmail.com>

RUN apk add zstd

RUN pip3 install httpx typing_extensions decorest

ADD main.py /root/main.py
RUN chmod +x /root/main.py

ENTRYPOINT ["/root/main.py"]