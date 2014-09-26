# This is a comment
FROM ubuntu:12.04
MAINTAINER Dan DiCara <ddicara@gnubio.com>
RUN apt-get -y update
RUN apt-get -y install build-essential python-dev
RUN apt-get -y install python-numpy 
RUN apt-get -y install python-scipy
RUN apt-get -y install python-yaml
RUN apt-get -y install python-pip
RUN easy_install -f http://biopython.org/DIST/ biopython

RUN echo 'HOSTNAME = 127.0.0.1' >>flaskr_settings.cfg
RUN export FLASKR_SETTINGS=/flaskr_settings.cfg

ADD . bioweb-api
WORKDIR bioweb-api
RUN pip install -r requirements.txt