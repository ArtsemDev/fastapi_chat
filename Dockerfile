FROM python:3.11.4

WORKDIR /chat

COPY ./requirements.txt /chat/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /chat/requirements.txt

COPY . /chat