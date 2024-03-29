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

from dotenv import load_dotenv
from sqlalchemy import create_engine
import sqlalchemy
from sqlalchemy.orm import sessionmaker


load_dotenv()
logger = logging.getLogger(__name__)
DB_PATH = os.getenv("DB_PATH")


class DBUtil:
    def __init__(self):
        try:
            SQLALCHEMY_DATABASE_URL = f"sqlite:///{DB_PATH}"
            engine = create_engine(
                SQLALCHEMY_DATABASE_URL
            )
            self.sessionLocal = sessionmaker(
                autocommit=False, autoflush=False, bind=engine)
        except Exception as err:
            logger.error(err)

    def __exec(self, query):
        try:
            db = self.sessionLocal()
            res = db.execute(query)
        except Exception as e:
            logging.error(e)
            raise e
        else:
            return list(map(dict, res))
        finally:
            db.close()

    def __exec_one(self, query):
        try:
            db = self.sessionLocal()
            res = db.execute(query)
        except Exception as e:
            logging.error(e)
            raise e
        else:
            return list(map(dict, res))[0]
        finally:
            db.close()

    def get(self, fields, table, condition=''):
        try:
            query = "select {} from {}".format(','.join(fields), table)
            if condition:
                query += (" where "+condition)
            return self.__exec_one(query)
        except Exception as err:
            logger.error(err)
            raise err

    def getAll(self, fields, table, condition=''):
        try:
            query = "select {} from {}".format(','.join(fields), table)
            if condition:
                query += (" where "+condition)
            return self.__exec(query)
        except Exception as err:
            logger.error(err)
            raise err

    def get_multi(self, keyName, keys, table):
        try:
            query = "select * from {} where {} in {}".format(table,
                                                             keyName, tuple(keys))
            return self.__exec(query)
        except Exception as err:
            logger.error(err)
            raise err

    def exec_Query(self, query):
        return self.__exec(query)
