""" This is a flask web application for Semantic Similarity with TF-Hub Universal Encoder """
from __future__ import absolute_import, division

import logging

import numpy as np
import tensorflow_hub as hub
from flask import Flask, request, abort

###################################################################################################
# Setting up flask app and cf environment.

APP = Flask(__name__)

###################################################################################################
# Getting the USE from data

MODULE_URL = "https://tfhub.dev/google/universal-sentence-encoder-large/5"


def embed_use(module: "The USE module URL to be used") -> "Embedding function":
    """Function so that one session can be called multiple times.
        Useful while multiple calls need to be done for embedding.
    """
    return hub.load(module)


# Import the Universal Sentence Encoder's TF Hub module
EMBED_FN = embed_use(MODULE_URL)


###################################################################################################
# End point to find similarity of the user query and return the simlarities.
@APP.route('/similarity', methods=['POST'])
def get_similarities():
    """ Refresh embeddings by passing the templates in HTTP POST request body """
    try:
        req_body = request.get_json()
        user_input = req_body["input_text"]
        list_titles = req_body["input_list"]
        embedded_input = EMBED_FN([user_input])[0]
        embedded_titles = EMBED_FN(list_titles)
        return {"d": dict(zip(list_titles, np.inner(embedded_titles, embedded_input).tolist()))}
    except Exception as err:
        return str(err)

###################################################################################################

# Main thread starts here


if __name__ == '__main__':
    APP.run()
