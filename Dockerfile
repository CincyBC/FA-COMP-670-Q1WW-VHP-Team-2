FROM python:3.11-slim-bullseye

RUN apt-get update && apt-get install -y \
    build-essential \
    python3-dev \
    apt-utils \
    python-dev \
    && apt-get autoremove -yqq --purge \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

RUN mkdir /app 
COPY ./app ./app
WORKDIR /app

EXPOSE 8000
CMD ["chainlit", "run", "app.py", "-w"]