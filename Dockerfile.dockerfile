
FROM python:3.11

RUN apt-get update
RUN apt-get install -y git

RUN git clone https://github.com/zolypka/traffic_check.git

WORKDIR /traffic_check

RUN pip install -r requirements.txt

CMD ["python", "main.py"]