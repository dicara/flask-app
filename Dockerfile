# This is a comment
FROM ddicara/bioweb
MAINTAINER Dan DiCara <ddicara@gnubio.com>

ADD . bioweb-api
WORKDIR bioweb-api
RUN pip install -r requirements.txt

CMD echo "DATABASE_URL='$MONGODB_PORT_27017_TCP_ADDR'" >>/flaskr_settings.cfg && python setup.py nosetests