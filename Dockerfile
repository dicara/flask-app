# This is a comment
FROM       gbsoftware/proprietary_base:latest
MAINTAINER Dan DiCara <ddicara@gnubio.com>

ENV FLASKR_SETTINGS /flaskr_settings.cfg

ADD     . bioweb-api
WORKDIR bioweb-api
RUN     pip install -r requirements.txt

CMD echo "DATABASE_URL='$MONGODB_DB_PORT_27017_TCP_ADDR'" >>/flaskr_settings.cfg && python setup.py nosetests --with-coverage --cover-package=bioweb_api --cover-html --cover-erase