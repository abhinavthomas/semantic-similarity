import logging
import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import mysql.connector

load_dotenv()
logger = logging.getLogger(__name__)


class DBUtil:
    def __init__(self):
        try:
            config = {
                'host': os.getenv('DB_HOST'),
                'user':  os.getenv('DB_USER'),
                'password':  os.getenv('DB_PASSWORD'),
                'database':  os.getenv('DB_SCHEMA'),
                'client_flags': [mysql.connector.ClientFlag.SSL]
            }

            if os.getenv('DEV'):
                dir_path = os.path.dirname(os.path.realpath(__file__))
                config['ssl_ca'] = os.path.join(
                    dir_path, 'BaltimoreCyberTrustRoot.crt.pem')

            SQLALCHEMY_DATABASE_URL = f"mysql+mysqlconnector://{config.get('user')}:{config.get('password')}@{config.get('host')}:{config.get('port') if 'port' in config else 3306}/{config.get('database')}"

            engine = create_engine(
                SQLALCHEMY_DATABASE_URL,
                pool_size=10,
                max_overflow=0,
                pool_recycle=3600
            )
            self.sessionLocal = sessionmaker(
                autocommit=False, autoflush=False, bind=engine)
        except mysql.connector.Error as err:
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
