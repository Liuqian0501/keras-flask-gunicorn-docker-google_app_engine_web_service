# google_app_engine_web_service

## step 1: enviroment
App engine requires libraries to be installed into a folder for deployment. You’ll download the `Gcloud Storage Client` as well.

```
$ mkdir google_app_engine_web_service
$ cd google_app_engine_web_service
$ git clone https://github.com/GoogleCloudPlatform/appengine-gcs-client.git
$ pip install -r requirements.txt -t lib
$ pip install GoogleAppEngineCloudStorageClient -t lib
```

local run appengine
```
>>> import sys
>>> import google
>>> gae_dir = google.__path__.append('/usr/local/google_appengine/google')
>>> sys.path.insert(0, gae_dir)
>>> import google.appengine
```


## step 2: `app.yaml` and `appengine_config.py`

app standard version
```
runtime: python27
api_version: 1
threadsafe: true
module: default
handlers:
- url: /.*
  script: main.app
```

## step 2:`config.py` and `storage.py`
store in bucket (you may need to create one)

`config.py`
```
PROJECT_ID = 'keraspredion'
CLOUD_STORAGE_BUCKET = 'kerasimagebucket'
MAX_CONTENT_LENGTH = 8 * 1024 * 1024
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
PREDICTION_SERVICE_URL = 'http://35.185.255.199:8080'
```



# step 3: `main.py` and templates


# step 4: test app


Cloud Shell lets you test your app before deploying to make sure it's running as intended, just like debugging on your local machine.

To test your app enter:
```
dev_appserver.py $PWD
```

# step 5: deploy
```
gcloud app deploy
```

