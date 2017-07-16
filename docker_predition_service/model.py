import numpy as np
import tensorflow as tf
import keras
from keras.preprocessing import image
from keras.applications.inception_v3 import preprocess_input, decode_predictions

model = keras.applications.inception_v3.InceptionV3(include_top=True, weights='imagenet', input_tensor=None, input_shape=None)
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
