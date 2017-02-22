FROM ubuntu:16.04
ENV PYTHONUNBUFFERED 1
MAINTAINER Elian Gidoni <elianmdp@gmail.com>
RUN apt-get update && apt-get install -y libjpeg-dev python python-pip libpq-dev python-dev postgresql-client git
RUN mkdir /project
WORKDIR /project
ADD requirements.txt /project/
RUN pip install -r requirements.txt
ADD . /project/
