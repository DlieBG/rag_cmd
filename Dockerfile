FROM python:3.11

WORKDIR /app/rag_cmd

COPY setup.py .
COPY src/ src/

RUN pip3 install -e .

ENV TZ=Europe/Berlin

WORKDIR /app
