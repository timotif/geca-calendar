FROM python:3.11.9-slim

RUN mkdir /app
COPY requirements.txt /app/requirements.txt
COPY . /app/

WORKDIR /app

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

CMD ["gunicorn", "-b", "0.0.0.0:8001", "main:app"]