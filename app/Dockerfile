FROM python:3.11.9-slim

RUN apt-get update && \
	apt-get upgrade -y && \
	rm -rf /var/lib/apt/lists/*

RUN mkdir -p /app/instance

COPY requirements.txt /app/requirements.txt
COPY . /app/

RUN pip install --upgrade pip
RUN pip install -r app/requirements.txt

CMD ["gunicorn", "-b", "0.0.0.0:8001", "app.app:app"]