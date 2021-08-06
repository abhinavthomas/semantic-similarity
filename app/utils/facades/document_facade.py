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

from typing import List, Optional, Tuple
from datetime import datetime

from pydantic.main import BaseModel
DB_SERVER = os.getenv('DB_SERVER')

if DB_SERVER == "MYSQL":
    from ..db.mysql import DBUtil
else:
    from ..db.sqlite import DBUtil

client = DBUtil()


class Document(BaseModel):
    id: int
    text: str


class Documents(BaseModel):
    docs: List[Document]


class Count(BaseModel):
    count: int


class DocumentFacade:
    store = 'document'

    @classmethod
    def get(self, id: int) -> Tuple[int, str]:
        doc = client.get(
            ['id', 'text'], self.store, 'id=' + str(id))
        return doc

    @classmethod
    def getAll(self) -> List[Tuple[int, str]]:
        _all_docs = client.getAll(
            ['id', 'text'], self.store)
        return _all_docs

    @classmethod
    def getCount(self) -> Count:
        _all_docs = client.get(
            'COUNT(id) as count', self.store)
        return _all_docs

    @classmethod
    def getAllDetailsIn(self, ids: List[int]) -> List[Document]:
        q = f"""SELECT FROM docs AS t1 WHERE t1.id in {tuple(ids)} ORDER BY FIELD(t1.id,{','.join(map(str,ids))})"""
        rows = client.exec_Query(q)
        return rows
