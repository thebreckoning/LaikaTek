FROM python:3.8-alpine

RUN apk --no-cache upgrade
RUN apk --no-cache add mariadb-connector-c-dev build-base libffi-dev
RUN pip install --upgrade pip
RUN pip install python-dotenv
RUN pip install flask
RUN pip install pymysql
RUN pip install azure-keyvault-secrets
RUN pip install azure-identity
RUN pip install azure-mgmt-keyvault


# Add Microsoft package repository
#RUN apk add --no-cache curl tar openssl sudo bash jq python3 py3-pip && \
#    apk --no-cache add --virtual=build gcc libffi-dev musl-dev openssl-dev make python3-dev && \
#    pip --no-cache-dir install azure-cli && \
#    apk del --purge build

WORKDIR /app

RUN pip install flask-login==0.6.2
RUN pip install flask-sqlalchemy==3.0.5
RUN pip install flask-wtf==1.1.1
#RUN pip install paho-mqtt
RUN pip install email_validator==2.0.0
RUN pip install gunicorn==21.2.0
RUN pip install Werkzeug
RUN pip install mariadb
RUN pip install flask-migrate

#COPY . /keymaster.py
COPY . /app

EXPOSE 8000

ENV FLASK_ENV=development

CMD ["gunicorn", "-b", "0.0.0.0:8000", "app:app", "--reload"]
