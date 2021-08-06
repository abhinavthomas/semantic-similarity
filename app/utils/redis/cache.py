import decimal
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
