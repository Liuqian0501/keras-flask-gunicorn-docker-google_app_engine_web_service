FROM ubuntu:latest

# Update python
RUN apt-get update --fix-missing
RUN apt-get install -y build-essential git
RUN apt-get install -y python python-dev python-setuptools

# Install virtualenv
RUN apt-get install -y python-pip python-virtualenv

# create virtual env and install dependencies
RUN virtualenv /opt/venv
ADD ./requirements.txt /opt/venv/requirements.txt
RUN /opt/venv/bin/pip install -r /opt/venv/requirements.txt

# Install nginx, supervisor, supervisor-stdout
RUN apt-get install -y nginx supervisor
RUN pip install supervisor-stdout
RUN service supervisor stop
RUN service nginx stop

# expose port
EXPOSE 80

# Add our config files
ADD ./supervisord.conf /etc/supervisord.conf
ADD ./nginx.conf /etc/nginx/nginx.conf

# Copy our service code
ADD ./prediction_service /opt/prediction_service

# start supervisor to run our wsgi server, nginx, supervisor-stdout
CMD supervisord -c /etc/supervisord.conf -n
