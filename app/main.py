#!/usr/bin/python

import asyncio
import logging
import os
import threading
from datetime import datetime
from typing import Dict, List, Optional, Tuple

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.params import Depends
import numpy as np
from app.auth.auth_bearer import JWTBearer
from app.utils import search as srch
from app.utils.facades.document_facade import Count, Document, DocumentFacade
from app.utils.redis.cache import RedisClient
from pydantic import BaseModel

load_dotenv()
logger = logging.getLogger(__name__)
UPDATE_AUTH_ROLE = os.getenv("UPDATE_AUTH_ROLE")
search_util = srch.SearchUtil()

redisClient = RedisClient()
app = FastAPI(title="Semantic Similarity Search",
              description="This service can be used for providing similar text based on semantic similarity using Universal Sentence Embeddings"
              )
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get('/', response_model=str)
def app_run_check():
    return 'Hello!'


@app.get('/similar/', response_model=List[Document])
def search(text: str, show: Optional[int] = 10) -> List[Document]:
    try:
        is_valid, error, query = _validate_request(text)
        if not is_valid:
            HTTPException(status_code=400, detail=error)
        else:
            if show:
                results = [id for id in search_util.search(query, int(show))]
            else:
                results = [id for id in search_util.search(query)]
            if len(results) > 0:
                resultsData = DocumentFacade.getAllDetailsIn(results)
    except Exception as error:
        logger.error(error)
        raise HTTPException(status_code=500, detail="Search failed")
    return resultsData


@app.get('/update_index/', response_model=Count, dependencies=[Depends(JWTBearer(applications=[UPDATE_AUTH_ROLE]))])
async def re_index() -> Count:
    try:
        Documents = DocumentFacade.getAll()
        DocumentIds, titles = zip(*[Document.values()
                                  for Document in Documents])
        asyncio.get_event_loop().create_task(search_util.index_items(DocumentIds, titles))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Updating failed"+str(e))
    return {'count': len(DocumentIds)}


class IndexStatus(BaseModel):
    DocumentsCount: int
    indexCount: int


@app.get('/get_index_status/', response_model=IndexStatus, dependencies=[Depends(JWTBearer(applications=[UPDATE_AUTH_ROLE]))])
def re_index() -> IndexStatus:
    DocumentsCount = DocumentFacade.getCount().get("count")
    indexCount = search_util.get_item_count()
    return {'DocumentsCount': DocumentsCount, "indexCount": indexCount}


@app.on_event("startup")
def update_index():
    try:
        Documents = DocumentFacade.getAll()
        DocumentIds, titles = zip(*[Document.values()
                                  for Document in Documents])
        asyncio.run(search_util.index_items(DocumentIds, titles))
    except Exception as e:
        logger.error('Error updating the index'+str(e))
    else:
        logger.info(
            str({'DocumentsCount': len(DocumentIds), 'time': datetime.now()}))
    finally:
        threading.Timer(int(os.getenv('UPDATE_INDEX_FREQ')),
                        update_index).start()


def _validate_request(text: str) -> Tuple[bool, Optional[str], Optional[np.ndarray]]:
    is_valid = False
    error = None
    query = None
    if text is None or len(text) < 2:
        error = 'Your search text is not valid'
    else:
        is_valid = True
        query = search_util.embed_util.extract_embeddings(text)
    return is_valid, error, query
