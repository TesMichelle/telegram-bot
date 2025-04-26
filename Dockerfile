FROM python:latest

WORKDIR /usr/src/not_bot/src
COPY src/* ./
COPY requirements.txt ./
RUN pip install -r requirements.txt

CMD ["python", "-u", "main.py"]