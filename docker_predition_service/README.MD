# `model.py`

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



