# This is a comment
FROM ubuntu:12.04
MAINTAINER Dan DiCara <ddicara@gnubio.com>
RUN apt-get -y update
RUN apt-get -y install build-essential python-dev
RUN apt-get -y install python-numpy 
RUN apt-get -y install python-scipy
RUN apt-get -y install python-yaml
RUN apt-get -y install python-pip
RUN apt-get -y install python-matplotlib
RUN easy_install -f http://biopython.org/DIST/ biopython

ENV FLASKR_SETTINGS /flaskr_settings.cfg

ADD     . bioweb-api
WORKDIR bioweb-api
RUN     easy_install -U distribute
RUN     pip install -r requirements.txt

CMD echo "DATABASE_URL='$MONGODB_DB_PORT_27017_TCP_ADDR'" >>/flaskr_settings.cfg && python setup.py nosetests