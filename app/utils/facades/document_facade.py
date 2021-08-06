#!/usr/bin/python
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
