# Main docker image
FROM python:3.8

# Enviroment variables
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

RUN mkdir /little_shelve
WORKDIR /little_shelve

# Installing OS Dependencies
RUN apt-get update && apt-get upgrade -y && apt-get install -y \
libsqlite3-dev
RUN pip install -U pip setuptools
COPY requirements.txt /little_shelve
COPY requirements-opt.txt /little_shelve/
COPY requirements-dev.txt /little_shelve/
RUN pip install -r /little_shelve/requirements.txt
RUN pip install -r /little_shelve/requirements-opt.txt
ADD . /little_shelve/

CMD python manage.py makemigrations && python manage.py migrate

# Django service port
EXPOSE 8000