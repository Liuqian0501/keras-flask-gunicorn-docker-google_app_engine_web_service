# 1. `model.py`

## Environment
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

## Keras applications
Keras Applications are deep learning models that are made available alongside pre-trained weights. These models can be used for prediction, feature extraction, and fine-tuning. Weights are downloaded automatically when instantiating a model.

### `InceptionV3`
we use 
`InceptionV3` (Inception V3 model), with weights pre-trained on ImageNet.

This model is available for both the Theano and TensorFlow backend, and can be built both with "channels_first" data format (channels, height, width) or "channels_last" data format (height, width, channels). The default input size for this model is 299x299.

```python
import keras
model = keras.applications.inception_v3.InceptionV3(include_top=True, weights='imagenet', input_tensor=None, input_shape=None)`
```

### `predict(image_file)`


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

# 2. `main.py`

## Environment
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

## `predict()`

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
  
connect and check
First, start the server. Then make a POST request to the prediction service
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
