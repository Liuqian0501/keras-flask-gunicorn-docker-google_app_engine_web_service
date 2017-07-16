# step 1: start a web service to predict

##  `model.py`

### Environment
```
pip install XXX
pip freeze > requirements.txt
```

```
requirement.txt

h5py==2.6.0
Keras==1.2.1
numpy==1.12.0
tensorflow==0.12.1
Pillow==4.0.0

```

### Keras applications
Keras Applications are deep learning models that are made available alongside pre-trained weights. These models can be used for prediction, feature extraction, and fine-tuning. Weights are downloaded automatically when instantiating a model.

#### `InceptionV3`
we use 
`InceptionV3` (Inception V3 model), with weights pre-trained on ImageNet.

This model is available for both the Theano and TensorFlow backend, and can be built both with "channels_first" data format (channels, height, width) or "channels_last" data format (height, width, channels). The default input size for this model is 299x299.

```python
import keras
model = keras.applications.inception_v3.InceptionV3(include_top=True, weights='imagenet', input_tensor=None, input_shape=None)`
```

#### `predict(image_file)`


```python
from keras.preprocessing import image
from keras.applications.inception_v3 import preprocess_input, decode_predictions
import tensorflow as tf
import numpy as np

graph = tf.get_default_graph()

def predict(image_file):
    img = image.load_img(image_file, target_size=(299, 299))
    input = image.img_to_array(img)
    input = np.expand_dims(input,axis=0)
    input = preprocess_input(input)

    global graph
    with graph.as_default():
        preds = model.predict(input)

    top3 = decode_predictions(preds,top=3)[0]

    predictions = [{'label': label, 'description': description, 'probability': probability * 100.0}
                    for label,description, probability in top3]
    return predictions



```

## `main.py`

### Environment
```
Flask==0.12
```

> We need current_app, this is useful for extensions that 
> want to support multiple applications running side by side. 

> we need request, The data from a client’s web page is sent 
> to the server as a global request object. In order to process 
> the request data,  it should be imported from the Flask module.

> We need to import the jsonify object, it will let us
> output json, and it will take care of the right string
> data conversion, the headers for the response, etc


```python
from flask import Flask, current_app, request, jsonify
import io
import model
import base64

app = Flask(__name__)
```

### `predict()`

```python
@app.route('/', methods=['POST'])
def predict():
    data = {}
    try:
        data = request.get_json()['data']
    except KeyError:
        return jsonify(status_code='400', msg='Bad Request'), 400

    data = base64.b64decode(data)  #Decode a Base64 encoded string.

    image = io.BytesIO(data)
    predictions = model.predict(image)
    current_app.logger.info('Predictions: %s', predictions)
    return jsonify(predictions=predictions)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5555, debug=True)
  ```
  
# Step 2. Test

First, start the server. Then make a POST request to the prediction service,use an external IP address
```sh
$ python main.py
(in another terminal window)

$ (echo -n '{"data": "'; base64 monkey.jpeg; echo '"}') | curl -X POST -H "Content-Type: application/json" -d @- http://35.197.11.221:5555
```

it should return
```json
{
  "predictions": [
    {
      "description": "macaque", 
      "label": "n02487347", 
      "probability": 80.617338418960571
    }, 
    {
      "description": "titi", 
      "label": "n02493509", 
      "probability": 2.7190608903765678
    }, 
    {
      "description": "langur", 
      "label": "n02488291", 
      "probability": 1.9507266581058502
    }
  ]
}
```


# step 3: use gunicorn to run the python web service

flask is not good enough for industry level.
## install gunicorn
```
pip install gunicorn
pip freeze > requirements.txt
```
use gunicorn as a wsgi container，and support python flask. This time we open port 8000.

## deploy with gunicorn
Run it in [prediction_service](/prediction_service) folder with gunicorn on 8000 using 4 workers
```
$: /opt/prediction/venv/bin/gunicorn -w4 -b0.0.0.0:8000 main:app
```
you will see
```
(venv) qian@webserver:~/prediction/docker_predition_service/prediction_service$ /opt/prediction/venv/bin/gunicorn -w4 -b0.0.0.0:8000 main:app
[2017-07-16 02:59:01 +0000] [15405] [INFO] Starting gunicorn 19.7.1
[2017-07-16 02:59:01 +0000] [15405] [INFO] Listening at: http://0.0.0.0:8000 (15405)
[2017-07-16 02:59:01 +0000] [15405] [INFO] Using worker: sync
[2017-07-16 02:59:01 +0000] [15410] [INFO] Booting worker with pid: 15410
[2017-07-16 02:59:01 +0000] [15413] [INFO] Booting worker with pid: 15413
[2017-07-16 02:59:01 +0000] [15414] [INFO] Booting worker with pid: 15414
[2017-07-16 02:59:01 +0000] [15415] [INFO] Booting worker with pid: 15415
Using TensorFlow backend.
Using TensorFlow backend.
Using TensorFlow backend.
Using TensorFlow backend.
```
## test it on port 8000
```sh
$ (echo -n '{"data": "'; base64 monkey.jpeg; echo '"}') | curl -X POST -H "Content-Type: application/json" -d @- http://35.197.11.221:8000
```

you will see result

```sh
{
  "predictions": [
    {
      "description": "macaque", 
      "label": "n02487347", 
      "probability": 80.617338418960571
    }, 
    {
      "description": "titi", 
      "label": "n02493509", 
      "probability": 2.7190608903765678
    }, 
    {
      "description": "langur", 
      "label": "n02488291", 
      "probability": 1.9507266581058502
    }
  ]
}
```

## kill gunicorn process
To end gunicorn process, need pid, take a lot of work. (no good!)
```
sudo pkill gunicorn 
```
- `pkill` - which will kill all processes matching the search text:

or
```
ps ax|grep gunicorn // show id
kill xxxx //where xxxx is the number in the first column
```

# step 4: use `supervisor` for process supervising

`supervisor`, A tool dedicated to managing the process, and you can manage the system's tooling process.

## install supervisor, supervisor_stdout 

```
pip install supervisor
pip freeze > requirements.txt
pip install supervisor-stdout
pip freeze > requirements.txt
```

## generate `supervisor.conf`
```
echo_supervisord_conf > supervisor.conf
nano supervisor.conf
```

append the follwing code to the end of `supervisor.conf`

```
[program:main]
command=/opt/venv/bin/gunicorn -w4 -b0.0.0.0:2170 main:app    ; supervisor set gunicorn to run main on 0.0.0.0:2170
startsecs=0                                                                     ; start time
stopwaitsecs=0                                                                  ; end wait time
autostart=true                                                                        
autorestart=true                                                                      
stdout_events_enabled = true
stderr_events_enabled = true

[eventlistener:stdout]
command = supervisor_stdout
buffer_size = 1000
events = PROCESS_LOG
result_handler = supervisor_stdout:event_handler
```

supervisor can mamage web，**edit** folowing

```conf
[inet_http_server]         ; inet (TCP) server disabled by default
port=0.0.0.0:9001        ; (ip_address:port specifier, *:port for all iface)
username=qian              ; (default is no username (open server))
password=0501               ; (default is no password (open server))

[supervisorctl]
serverurl=unix:///tmp/supervisor.sock ; use a unix:// URL  for a unix socket
serverurl=http://0.0.0.0:9001 ; use an http:// url to specify an inet socket
username=qian              ; should be same as http_username if set
password=0501               ; should be same as http_password if set
;prompt=mysupervisor         ; cmd line prompt (default "supervisor")
;history_file=~/.sc_history  ; use readline history if available

[supervisord]
logfile=/tmp/supervisord.log ; main log file; default $CWD/supervisord.log
logfile_maxbytes=50MB        ; max main logfile bytes b4 rotation; default 50MB
logfile_backups=10           ; # of main logfile backups; 0 means none, default 10
loglevel=info                ; log level; default info; others: debug,warn,trace
pidfile=/tmp/supervisord.pid ; supervisord pidfile; default supervisord.pid
nodaemon= true               ; start in foreground if true; default false
minfds=1024                  ; min. avail startup file descriptors; default 1024
minprocs=200                 ; min. avail process descriptors;default 200
```

## start supervisord

`supervisord -c supervisor.conf `


# step 5: set up nginx

## install nginx in sudo mode
```
sudo apt-get install nginx
```

## edit `nginx.conf`
edit your `nginx.conf` in `/etc/nginx`


### structral of `nginx.conf`
<p align = center>
<img src = http://upload-images.jianshu.io/upload_images/1174946-8c76b97959081037.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240>
<p>

### HTML use of `nginx.conf`
<p align = center>
 <img src = http://upload-images.jianshu.io/upload_images/1174946-8dfefd1561cd3635.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240>
<p>

`nginx.conf`

```
user www-data;
worker_processes 1;
pid /var/run/nginx.pid;
daemon off;

events {
    worker_connections 768;
    # multi_accept on;
}
http {
    ##
    # Basic Settings
    ##
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;
    include /etc/nginx/mime.types;
    default_type application/octet-stream;
    ##
    # Logging Settings
    ##
    access_log /dev/stdout combined;
    error_log /dev/stdout info;
    
    # Virtual Host Configs
    ##
    
    upstream app_server {
            # For a TCP configuration:
            server 0.0.0.0:2170 fail_timeout=0;
    }

    server{
        listen 0.0.0.0:8080;
        client_max_body_size 4G;
        
        location / {
            proxy_pass http://app_server;
            proxy_redirect off;
            proxy_set_header Host $host:8080;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        }
	}
}
```
## Worker Processes
In `/etc/nginx/nginx.conf`, set `worker_processes` 1; if you have a lower traffic site where nginx, a database, and a web application all run on the same server.

If you have a higher traffic site or a dedicated instance for nginx, set one worker per CPU core: worker_processes auto;



```
$: /home/qian/prediction/venv/bin/gunicorn -w4 -b0.0.0.0:2170 main:app
then 
$: /usr/sbin/nginx
```

append following to `supervisord.conf`
```
[program:nginx]
command=/usr/sbin/nginx
startsecs=0
stopwaitsecs=0
autostart=true
autorestart=true
stdout_events_enabled = true
stderr_events_enabled = true
```

nginx is install by sudo，we run nginx in root mode，so we need to run root supervisor

```
sudo supervisord -c supervisor.conf
```



# step 6: docker it

create `Dockerfile`

```
FROM ubuntu:latest

# Update python, Install virtualenv, nginx, supervisor
RUN apt-get update --fix-missing  \
        && apt-get install -y build-essential git \
        && apt-get install -y python python-dev python-setuptools \
        && apt-get install -y python-pip python-virtualenv \
        && apt-get install -y nginx supervisor

RUN service supervisor stop \
        && service nginx stop

# create virtual env and install dependencies
RUN virtualenv /opt/venv
ADD ./requirements.txt /opt/venv/requirements.txt
RUN /opt/venv/bin/pip install -r /opt/venv/requirements.txt

# expose port
EXPOSE 8080 9001

RUN pip install supervisor-stdout

# Add our config files
ADD ./supervisor.conf /etc/supervisor.conf
ADD ./nginx.conf /etc/nginx/nginx.conf

# Copy our service code
ADD ./prediction_service /opt/prediction_service

# start supervisor to run our wsgi server, nginx, supervisor-stdout
CMD supervisord -c /etc/supervisor.conf -n
```
## build docker image
```
#/bin/sh
docker build -t prediction-service .
```
## Share your image
The notation for associating a local image with a repository on a registry is username/repository:tag. The tag is optional, but recommended, since it is the mechanism that registries use to give Docker images a version. Give the repository and tag meaningful names for the context,

Now, put it all together to tag the image. Run docker tag image with your username, repository, and tag names so that the image will upload to your desired destination. The syntax of the command is:

```
docker tag prediction-service gcr.io/PROJECT_ID/prediction-service
gcloud docker -- push gcr.io/PROJECT_ID/prediction-service
```

## download shared imges and run it

install docker, download imges, run docker imges
```sh
curl -sSL https://get.docker.com | sh
sudo gcloud docker -- pull gcr.io/PROJECT_ID/prediction_service:latest
sudo docker run -td -p 8080:8080 -p 9001:9001 gcr.io/PROJECT_ID/prediction-service
```
## manipulate running docker container
```sh
docker build -t friendlyname .  # Create image using this directory's Dockerfile
docker run -p 4000:80 friendlyname  # Run "friendlyname" mapping port 4000 to 80
docker run -d -p 4000:80 friendlyname         # Same thing, but in detached mode
docker ps                                 # See a list of all running containers
docker stop <hash>                     # Gracefully stop the specified container
docker ps -a           # See a list of all containers, even the ones not running
docker kill <hash>                   # Force shutdown of the specified container
docker rm <hash>              # Remove the specified container from this machine
docker rm $(docker ps -a -q)           # Remove all containers from this machine
docker images -a                               # Show all images on this machine
docker rmi <imagename>            # Remove the specified image from this machine
docker rmi $(docker images -q)             # Remove all images from this machine
docker login             # Log in this CLI session using your Docker credentials
docker tag <image> username/repository:tag  # Tag <image> for upload to registry
docker push username/repository:tag            # Upload tagged image to registry
docker run username/repository:tag                   # Run image from a registry
```








