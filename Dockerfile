FROM python:3

RUN apt-get update && apt-get -y install netcat && apt-get clean

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY config.yaml ./
COPY run.sh ./

COPY player/ ./player/

RUN chmod +x ./run.sh
EXPOSE 8080

CMD ["./run.sh"]