FROM python:3.8-alpine

RUN apk --no-cache upgrade
RUN apk --no-cache add mariadb-connector-c-dev build-base libffi-dev
RUN pip install --upgrade pip
RUN pip install python-dotenv
RUN pip install flask
RUN pip install pymysql

WORKDIR /app


# This will be moved into the requirements.txt file eventually. Keeping here for now for ease of development.
RUN pip install flask-login==0.6.2
RUN pip install flask-sqlalchemy==3.0.5
RUN pip install flask-wtf==1.1.1
RUN pip install paho-mqtt==1.6.1
RUN pip install email_validator==2.0.0
RUN pip install gunicorn==21.2.0
RUN pip install Werkzeug
RUN pip install mariadb
RUN pip install flask-migrate

COPY . /app

EXPOSE 8000

ENV FLASK_ENV=development

CMD ["gunicorn", "-b", "0.0.0.0:8000", "app:app", "--reload"]