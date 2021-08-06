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
import tempfile
from collections import OrderedDict
from typing import Dict, List

import numpy as np
from annoy import AnnoyIndex

VECTOR_LENGTH = int(os.getenv('EMBEDDING_DIM'))
N_TREES = int(os.getenv('N_TREES'))

logger = logging.getLogger(__name__)


class MatchingUtil:

    def __init__(self, index_file):
        self.__index_file = index_file
        self.__load_index__()

    def __load_index__(self):
        logger.info('Initialising matching utility...')
        self.__index = AnnoyIndex(VECTOR_LENGTH, metric='angular')
        self.__index.load(self.__index_file, prefault=True)

        logger.info('Annoy index {} is loaded'.format(self.__index_file))
        with open(self.__index_file + '.mapping', 'rb') as handle:
            self.__mapping = pickle.load(handle)
        logger.info('Mapping file {} is loaded'.format(
            self.__index_file + '.mapping'))
        self.__index_mapping = dict()
        for item_id in self.__mapping.keys():
            self.__index_mapping[self.__mapping.get(
                item_id).get('index')] = item_id
        logger.info('Matching utility initialised.')

    def find_similar_items(self, vector, num_matches) -> List[int]:
        index_ids = self.__index.get_nns_by_vector(
            vector, num_matches, search_k=-1, include_distances=False)
        identifiers = [self.__index_mapping.get(
            index_id) for index_id in index_ids]
        return identifiers

    def get_item(self, item_id: int) -> Dict:
        return self.__mapping.get(item_id)

    def get_item_count(self):
        return self.__index.get_n_items()

    def rebuild_index(self, items: List[int], texts: List[str], embeddings: List[np.ndarray]):
        try:
            __temp_index = AnnoyIndex(VECTOR_LENGTH, metric='angular')
            __temp_mapping = OrderedDict()
            for _i, _item in enumerate(items):
                __temp_index.add_item(_i, embeddings[_i])
                __temp_mapping[_item] = {
                    'index': _i, 'text': texts[_i], 'embedding': embeddings[_i]}

            logger.info('A total of {} items added to the index'.format(_i))
            logger.info('Building the index with {} trees...'.format(N_TREES))
            __temp_index.build(n_trees=N_TREES)
            logger.info('Index is successfully built.')

            logger.info('Saving index to disk...')
            with tempfile.TemporaryFile() as fp:
                __temp_index.save(str(fp.name))
                self.__index_file = str(fp.name)
            logger.info('Index is saved to disk.')
            logger.info("Index file size: {} GB".format(
                round(os.path.getsize(self.__index_file) / float(1024 ** 3), 2)))
            logger.info('Saving mapping to disk...')
            with open(self.__index_file + '.mapping', 'wb') as handle:
                pickle.dump(__temp_mapping, handle,
                            protocol=pickle.HIGHEST_PROTOCOL)
            logger.info('Mapping is saved to disk.')
            logger.info("Mapping file size: {} MB".format(
                round(os.path.getsize(self.__index_file + '.mapping') / float(1024 ** 2), 2)))
        except Exception as e:
            logger.error("Error updating index "+str(e))
            raise e
        else:
            self.__load_index__()
            return str(self.__index_file)

    def find_similar_vectors(self, vector, num_matches) -> List[np.array]:
        items = self.find_similar_items(vector, num_matches)
        vectors = [np.array(self.__index.get_item_vector(item))
                   for item in items]
        return vectors
