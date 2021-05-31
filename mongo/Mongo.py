from pymongo import MongoClient
import yaml
import pathlib

class MongoDB(object):
    def __init__(self, database_name=None, collection_name=None):
        with open(str(pathlib.Path(__file__).parent.absolute())+'/credentials.yaml') as f:
            docs = yaml.load(f)
        # connecting to mongodb atlas cloud cluster
        url = docs['client'].format(password=docs['password'],database_name=database_name)
        try:
            self._client = MongoClient(url)
        except Exception as error:
            print(Exception(error))
        self._database = self._client[database_name]
        self._collection = self._database[collection_name]

    def insert(self, post):
        post_ids = []
        try:
            post_ids = self._collection.insert_many(post, ordered=False).inserted_ids
        except Exception as error:
            print(Exception(error))
        return post_ids

    def find(self, query=None):
        return self._collection.find(query)


