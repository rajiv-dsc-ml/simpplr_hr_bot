#syntax = docker/dockerfile:experimental
FROM python:3.11.9

WORKDIR /var/www

# This prevents Python from writing out pyc files
ENV PYTHONDONTWRITEBYTECODE 1
# This keeps Python from buffering stdin/stdout
ENV PYTHONUNBUFFERED 1

# install system dependencies
RUN apt-get update \
    && apt-get -y install gcc make vim wget curl unixodbc-dev

# Install Tesseract
RUN apt-get install -y \
    tesseract-ocr \
    libtesseract-dev \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

# install dependencies
RUN pip install --no-cache-dir --upgrade pip

COPY ./requirements.txt ./requirements.txt
RUN --mount=type=cache,mode=0755,target=/root/.cache/pip pip install -r requirements.txt

COPY . .
#RUN chmod a+x /var/www/data_upserted.py
#RUN python /var/www/data_upserted.py
RUN chmod a+x ./docker-entry.sh

EXPOSE 8087

ENTRYPOINT ["./docker-entry.sh"]
