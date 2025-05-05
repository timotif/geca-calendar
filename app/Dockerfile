FROM python:3.11.9-slim

RUN apt-get update && \
	apt-get upgrade -y && \
	rm -rf /var/lib/apt/lists/*

RUN mkdir -p /app/instance

COPY requirements.txt /app/requirements.txt
COPY . /app/

RUN pip install --upgrade pip
RUN pip install -r app/requirements.txt

WORKDIR /app

ARG PORT=8001
ENV PORT=${PORT}

CMD ["sh", "-c", "gunicorn -b 0.0.0.0:${PORT} --timeout 120 app:app"]