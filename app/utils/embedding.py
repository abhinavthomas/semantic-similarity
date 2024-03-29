#!/usr/bin/python
# Semantic similarity implementation.

# Provides a fast api,for semantic similarity search using Spotify Annoy and Universal Sentence Encoder.

# Copyright (c) Abhinav Thomas.

# semantic-similarity is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# semantic similarity is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with semantic-similarity.  If not, see <https://www.gnu.org/licenses/>.
import logging
import os
import pickle
from typing import List, Optional, Union

import numpy as np

import tensorflow_hub as hub
from dotenv import load_dotenv
import tensorflow as tf
load_dotenv()

logger = logging.getLogger(__name__)

MODULE_URL = os.getenv('MODULE_URL')


class EmbedUtil:

    def __init__(self, random_vector_file: os.PathLike):
        if os.path.exists(random_vector_file):
            logger.info("Loading random projection matrix...")
            with open(random_vector_file, 'rb') as handle:
                self.random_projection_matrix = pickle.load(handle)
        logger.info('random projection matrix is loaded.')
        logger.info('Initialising embedding utility...')
        embed = hub.load(MODULE_URL)
        logger.info('tf.Hub module is loaded.')

        def _embeddings_fn(sentences: List[str]) -> tf.SparseTensor:
            computed_embeddings = embed(sentences)
            return computed_embeddings

        self.embedding_fn = _embeddings_fn
        logger.info('Embedding utility initialised.')

    def extract_embeddings(self, query: str) -> np.ndarray:
        '''Generates the embedding for the query'''
        query_embedding = self.embedding_fn([query])[0].numpy()
        if self.random_projection_matrix is not None:
            query_embedding = query_embedding.dot(
                self.random_projection_matrix)
        return query_embedding

    def extract_embeddings_multi(self, queries: List[str]) -> Union[np.ndarray, List[np.ndarray]]:
        '''Generates the embedding for the queries'''
        text_embeddings = self.embedding_fn(queries)
        query_embeddings = []
        if self.random_projection_matrix is not None:
            for text_embedding in text_embeddings:
                text_embedding.dot(self.random_projection_matrix)
                query_embeddings.append(text_embedding)
        return query_embeddings
