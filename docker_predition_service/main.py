# coding: utf-8

# We need current_app, this is useful for extensions that 
# want to support multiple applications running side by side.

# we need request, The data from a client’s web page is sent 
# to the server as a global request object. In order to process 
# the request data, it should be imported from the Flask module.

# We need to import the jsonify object, it will let us
# output json, and it will take care of the right string
# data conversion, the headers for the response, etc

from flask import Flask, current_app, request, jsonify
import io
import model
import base64

app = Flask(__name__)


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
