#Semantic Similarity

The semsim is Python3 based web application(Flask - API) that can be used to identify the semantic similarity between agiven input text and a set of inputs. Semantic similarity is a measure of the degree to which two pieces of text carry the same meaning. This is broadly useful in obtaining good coverage over the numerous ways that a thought can be expressed using language without needing to manually enumerate them. 

![Semantic Similarity](https://www.gstatic.com/aihub/tfhub/universal-sentence-encoder/example-similarity.png)

We make use of Universal Sentence Encoder model Large 5.
This module is about 800MB. Depending on your network speed, it might take a while to load the first time you instantiate it. After that, loading the model should be faster as modules are cached by default [learn more about caching](https://www.tensorflow.org/hub/tf2_saved_model). Further, once a module is loaded to memory, inference time should be relatively fast.

Please see [Universal Sentence Encoder 4](https://tfhub.dev/google/universal-sentence-encoder/4) for details about the embedding

Currently the API end points are:

* /similarity: Find similarity between the input text and list of texts and returns a json with texts as keys and similairty as value.

## How to Contribute to this Project

Follow the steps described in [CONTRIBUTE.md](CONTRIBUTE.md)

## How to use the latest version

* Run the application locally:
  + Installing the required libraries.

  

``` bash
  pip install -r requirements.txt
  ```

  + running the developement server

  

``` python
  python app.py
  ```

### Request parameters and body for the endpoints

1. **/similarity/**
  1. Params: None
  2. Body :

``` json
        {
    "input_text": "restart system",
    "input_list": [
        "I like my phone",
        "restart system",
        "System restart",
        "system restart",
        "systems restart",
        "My phone is not good.",
        "Your cellphone looks great.",
        "Will it snow tomorrow?"
    ]
}
```

Response: 

``` json
    {"d": {"I like my phone": 0.05919026955962181,
  "My phone is not good.": 0.0359722301363945,
  "System restart": 0.8752236366271973,
  "Will it snow tomorrow?": 0.03468877077102661,
  "Your cellphone looks great.": -0.029877029359340668,
  "restart system": 1.0,
  "system restart": 0.8752236366271973,
  "systems restart": 0.7790520787239075}}
```

## Tests

No parts of the code are covered with tests.
