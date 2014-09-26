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

ADD . bioweb-api
WORKDIR bioweb-api
RUN pip install -r requirements.txt

CMD echo "HOSTNAME='$MONGODB_PORT_27017_TCP_ADDR'" >>/bioweb-api/flaskr_settings.cfg && export FLASKR_SETTINGS=/bioweb-api/flaskr_settings.cfg && python setup.py nosetests