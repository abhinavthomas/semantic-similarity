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
from . import embedding, matching
from dotenv import load_dotenv
from typing import List
import os
import logging
STORAGE = os.getenv('STORAGE')

if STORAGE == "AZURE":
    from app.utils.storage.azure_storage import download_artefacts, upload_artefacts
else:
    def download_artefacts(blob_name: str, local_file: str):
        # TO-DO Write your own storage logic
        pass

    def upload_artefacts(blob_name: str, local_file: str):
        # TO-DO Write your own storage logic
        pass

load_dotenv()
logger = logging.getLogger(__name__)
INDEX_FILE = os.getenv('ANNOY_INDEX_FILE_NAME')
RANDOM_VECTOR_FILE = os.getenv('RANDOM_VECTOR_FILE_NAME')
TABLE_NAME = os.getenv('DB_TABLE')


class SearchUtil:

    def __init__(self):

        logger.info('Initialising search utility...')

        dir_path = os.path.dirname(os.path.realpath(__file__))
        # dir_path = os.path.join(dir_path, 'models')
        index_file = INDEX_FILE
        # index_file = os.path.join(dir_path, INDEX_FILE)
        random_vector_file = RANDOM_VECTOR_FILE
        # random_vector_file = os.path.join(dir_path, RANDOM_VECTOR_FILE)

        # if not os.getenv('DEV'):
        logger.info('Downloading index artefacts...')
        download_artefacts(INDEX_FILE, index_file)
        download_artefacts(INDEX_FILE+".mapping", index_file+".mapping")
        logger.info('Index artefacts downloaded.')

        logger.info('Downloading random_vector artefacts...')
        download_artefacts(RANDOM_VECTOR_FILE, random_vector_file)
        logger.info('Index artefacts downloaded.')

        logger.info('Initialising matching util...')
        self.match_util = matching.MatchingUtil(index_file)
        logger.info('Matching util initialised.')

        logger.info('Initialising embedding util...')
        self.embed_util = embedding.EmbedUtil(random_vector_file)
        logger.info('Embedding util initialised.')

        logger.info('Search utility is up and running.')

    def searchable(self, item_id: int):
        return self.match_util.get_item(item_id)

    @classmethod
    def __upload_index__(cls, index_loc):
        # dir_path = os.path.join(dir_path, 'models')
        index_file = index_loc
        random_vector_file = RANDOM_VECTOR_FILE
        # random_vector_file = os.path.join(dir_path, RANDOM_VECTOR_FILE)
        logger.info('Uploading index artefacts...')
        upload_artefacts(INDEX_FILE, index_file)
        upload_artefacts(INDEX_FILE+".mapping", index_file+".mapping")
        logger.info('Index artefacts uploaded.')

        logger.info('Uploading random_vector artefacts...')
        upload_artefacts(RANDOM_VECTOR_FILE, random_vector_file)
        logger.info('random_vector artefact uploaded.')

    async def index_items(self, items: List[int], texts: List[str]):
        try:
            query_embeddings = []
            for _i, _item in enumerate(items):
                emb = self.match_util.get_item(_item)
                if emb == None:
                    emb = self.embed_util.extract_embeddings(texts[_i])
                else:
                    emb = emb.get('embedding')
                query_embeddings.append(emb)
            index_loc = self.match_util.rebuild_index(
                items, texts, query_embeddings)
        except Exception as e:
            logger.error(str(e))
        else:
            SearchUtil.__upload_index__(index_loc)

    def search(self, item, num_matches=10):
        query_embedding = item.get('embedding')
        item_ids = self.match_util.find_similar_items(
            query_embedding, num_matches)
        return item_ids

    def get_item_count(self):
        return self.match_util.get_item_count()


if __name__ == '__main__':
    SearchUtil.__upload_index__(INDEX_FILE)
