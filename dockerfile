FROM python:3.8-alpine

RUN apk --no-cache upgrade
RUN apk --no-cache add mariadb-connector-c-dev build-base libffi-dev
RUN pip install --upgrade pip

# Set the working directory
WORKDIR /app

# Copy the requirements.txt file into the container
COPY requirements.txt .

# Install the Python packages
RUN pip install --no-cache-dir -r requirements.txt
RUN pip show Flask-Login
# Copy the rest of the application into the container
COPY . /app

EXPOSE 8000

ENV FLASK_ENV=development

CMD ["gunicorn", "-b", "0.0.0.0:8000", "app:app", "--reload"]
