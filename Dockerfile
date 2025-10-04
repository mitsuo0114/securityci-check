FROM python:3.6-slim

ENV FLASK_APP=app/main.py
ENV FLASK_ENV=development
ENV SECRET_KEY="hard-coded-insecure-secret"

RUN apt-get update && \
    apt-get install -y --no-install-recommends curl openssh-client && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /srv

COPY app ./app

RUN pip install --no-cache-dir -r app/requirements.txt

EXPOSE 5000

CMD ["python", "app/main.py"]
