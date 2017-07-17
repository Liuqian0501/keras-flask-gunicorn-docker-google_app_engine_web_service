import config
import logging
from flask import current_app, Flask, render_template, request
from google.appengine.api import images
from google.appengine.ext import blobstore
import urllib2
import storage
import base64
import json
from model import firebase_api as fb
import pytz
import os
import time
import datetime


app = Flask(__name__)
app.config.from_object(config)
logging.basicConfig(level=logging.INFO)


def upload_image_file(stream, filename, content_type):
    if not stream:
        return None


    bucket_filepath = storage.upload_file(
        stream,
        filename,
        content_type
    )


    logging.info(
        "Uploaded file %s as %s.", filename, bucket_filepath)

    blobstore_filename = '/gs{}'.format(bucket_filepath)
    blob_key = blobstore.create_gs_key(blobstore_filename)
    img_url = images.get_serving_url(blob_key, secure_url=True)
    return img_url


def fetch_predictions(img_stream):
    predictions = {}
    server_url = current_app.config['PREDICTION_SERVICE_URL']
    req = urllib2.Request(server_url, json.dumps({'data': base64.b64encode(img_stream)}),
                          {'Content-Type': 'application/json'})
    try:
        f = urllib2.urlopen(req)
        predictions = json.loads(f.read())
    except urllib2.HTTPError as e:
        logging.exception(e)

    logging.info('Predictions: %s', predictions)

    return predictions

def get_firebase_url(database):
    url = '%s/%s.json' % (config.FIREBASE_URL, database)
    return url


def dump_result(bucket_filepath, predictions, image_url):
    timestamp = time.time()
    filename = bucket_filepath.split('/')[-1].split('.')[0]
    # st = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
    result = {
        filename: {
            'predictions': predictions,
            'image_url': image_url,
            'create_timestamp': timestamp
            }
        }
    return json.dumps(result)

def fetch_recent_results():
    url = '%s?orderBy="create_timestamp"&limitToLast=10&print=pretty' % get_firebase_url('results')
    content = fb.firebase_get(url)
    results = []
    if not content:
        return results
    for key, value in content.iteritems():
        create_date = datetime.datetime.fromtimestamp(value['create_timestamp'])
        create_date = pytz.utc.localize(create_date)
        value['create_date'] = create_date.astimezone(pytz.timezone('America/Chicago')).strftime("%Y-%m-%d %H:%M:%S")
        results.append(value)

    results = sorted(results, key=lambda r: r['create_timestamp'], reverse=True)
    for result in results:
        logging.info(result['create_date'])
    return results

@app.route('/', methods=['GET', 'POST'])
def main():
    if request.method == 'POST':
        img = request.files.get('image')

        img_stream = img.read()
        filename = img.filename
        content_type = img.content_type
        img_url = upload_image_file(img_stream, filename, content_type)

        predictions = fetch_predictions(img_stream=img_stream)

        return render_template('view.html', image_url=img_url, predictions=predictions['predictions'])
    return render_template('form.html')


@app.errorhandler(500)
def server_error(e):
    logging.error('An error occurred during a request.')
    return 'An internal error occurred.', 500
