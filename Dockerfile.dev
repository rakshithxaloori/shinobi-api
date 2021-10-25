# pull the official base image
FROM python:3.9

# set work directory
WORKDIR /usr/src/app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install dependencies
RUN pip3 install --upgrade pip
COPY requirements.txt /usr/src/app/
RUN pip3 install -r requirements.txt

# copy project
COPY . /usr/src/app/
