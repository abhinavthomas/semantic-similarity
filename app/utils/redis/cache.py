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
 
import json
import os
from typing import List
from fastapi.encoders import jsonable_encoder
from dotenv import load_dotenv

from redis import StrictRedis

load_dotenv()


class RedisClient:

    def __init__(self):
        "Return the redis client object"
        self.rClient = StrictRedis(host=os.getenv('REDIS_HOST'), port=os.getenv('REDIS_PORT'),
                                   password=os.getenv("REDIS_KEY"), ssl=True)
        self.preKey = os.getenv('REDIS_PRE_KEY')

    def get(self, key: str) -> List:
        res = self.rClient.get(self.preKey+key)
        if res is not None:
            res = json.loads(res)
        return res

    def set(self, key: str, value: List[dict]) -> bool:
        value = jsonable_encoder(value)
        return self.rClient.set(self.preKey+key, json.dumps(value), 3600)
