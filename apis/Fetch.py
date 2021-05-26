from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from apis.APIKey import APIKey

class Fetch:
  def __init__(self, youtube_api_service_name=None, youtube_api_version=None):
    self.youtube_api_service_name = youtube_api_service_name
    self.youtube_api_version = youtube_api_version
    self.api_key = APIKey()
    self.developer_key=self.api_key.get_next_key()
    self.youtube=build(self.youtube_api_service_name, self.youtube_api_version,
      developerKey=self.developer_key)

  def youtube_fetch(self, args):

    # Call search.list method to retrieve results matching the specified
    # query term.
    try:
      search_response = self.youtube.search().list(
        q=args['q'],
        part='id,snippet',
        type='video',
        order='date',
        publishedAfter=args['published_after'],
        maxResults = 50
      ).execute()
    except HttpError as e:
      # This means API key has expired. We fetch the next key available from db when his happens.
      if e.status_code == 403:
        self.developer_key = self.api_key.get_next_key()
        self.youtube = build(self.youtube_api_service_name, self.youtube_api_version,
                             developerKey=self.developer_key)
        return self.youtube_fetch(args)
      print(e)
      return -1
    except Exception as e:
      print(e)
      return -1

    return search_response
