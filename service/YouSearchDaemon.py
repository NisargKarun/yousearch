from apis.Fetch import Fetch
from mongo.Mongo import MongoDB
from time import sleep
import datetime
import random

def getQueries():
    db = MongoDB(database_name='you_search', collection_name='queries')
    queryFetch = db.find()
    queries = []
    for query in queryFetch:
        queries.append({'query':query['query'],'nextPageToken':None})
    random.shuffle(queries)
    return queries


class YouSearchDaemon():
    keepRunning = True

    def __init__(self):
        self.db = MongoDB(database_name='you_search', collection_name='videos')
        self.fetch = Fetch(youtube_api_service_name = 'youtube', youtube_api_version = 'v3')
        self.queries = getQueries()

    def start(self, sleepTime=10):
        YouSearchDaemon.keepRunning = True
        queryIndex = 0
        while(YouSearchDaemon.keepRunning):
            try:
                args = {}
                args['q'] = self.queries[queryIndex]['query']
                if self.queries[queryIndex]['nextPageToken'] is None:
                    args['published_after'] = (datetime.datetime.today() - datetime.timedelta(days=1)).isoformat() + "Z"
                search_response = self.fetch.youtube_fetch(args)
                if(search_response != -1):
                    self.writeResultsToDb(search_response)
                queryIndex = (queryIndex+1) % len(self.queries)
                sleep(sleepTime)
            except Exception as error:
                print(Exception(error))

    @staticmethod
    def stopDaemon():
        YouSearchDaemon.keepRunning = False

    def writeResultsToDb(self, search_response):
        videos = list()
        for item in search_response['items']:
            videos.append({'videoId': item['id']['videoId'], 'publishedAt': item['snippet']['publishedAt'], 'title': item['snippet']['title'],
                           'description': item['snippet']['description'], 'channelTitle': item['snippet']['channelTitle'],
                           'thumbnail': item['snippet']['thumbnails']['default']})

        self.db.insert(videos)
