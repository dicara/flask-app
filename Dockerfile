# This is a comment
FROM       swi-03.global.bio-rad.com/gbsoftware/proprietary_base:latest
MAINTAINER Dan DiCara <ddicara@gnubio.com>

ENV FLASKR_SETTINGS /flaskr_settings.cfg

ADD     . bioweb-api
WORKDIR bioweb-api
RUN     pip install -r requirements.txt

RUN     apt-get update && apt-get -y install cron
RUN     crontab update_reports_cron

CMD echo "DATABASE_URL='$MONGODB_DB_PORT_27017_TCP_ADDR'" >>/flaskr_settings.cfg && python setup.py nosetests
