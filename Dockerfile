FROM python:3.11.9-slim

RUN mkdir /app


COPY requirements.txt /app/requirements.txt
COPY . /app/

WORKDIR /app

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Debug info
RUN python -V
RUN pip list

RUN apt update && apt install -y gunicorn

CMD ["gunicorn", "-b", "0.0.0.0:8080", "main:app"]
# CMD ["tail", "-f", "/dev/null"]