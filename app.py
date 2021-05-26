from bson import json_util
from flask import Flask, render_template, request, jsonify, Response
from service.YouSearchDaemon import YouSearchDaemon

from threading import Thread
from mongo.Mongo import MongoDB

app = Flask(__name__)

db = MongoDB(database_name='you_search', collection_name='videos')

@app.route("/", methods=['GET'])
def welcome():
    Thread(target=startYouSearchDaemon).start()
    return "Welcome to YouSearch!"

# Fetches the latest YouTube videos stored in the database. Uses keyset pagination to fetch older data.
@app.route("/youtube/videos/", methods=['GET'])
def fetchVideos():
    page_token = request.args.get('pageToken')
    limit = min(request.args.get('limit', type = int) or 10, 10)
    myquery =  {"publishedAt": { "$lt": page_token } } if page_token else None
    video_list = list(db.find(myquery).sort([('publishedAt' , -1)]).limit(limit))
    if not video_list:
        return Response(json_util.dumps({}),mimetype='application/json')
    for video in video_list:
        video.pop('_id')
        videoLink = video.pop('videoId')
        video['videoLink'] = "https://www.youtube.com/watch?v=" + videoLink
    if len(video_list) < limit:
        return Response(
            json_util.dumps({'videos': video_list}),
            mimetype='application/json'
        )
    return Response(
        json_util.dumps({'videos': video_list, 'nextPageToken': video_list[-1]['publishedAt']}),
        mimetype='application/json'
    )

# Fetches the YouTube videos stored in the database whose title or description contains any of the words provided in the search key.
@app.route("/youtube/search/", methods=['GET'])
def searchVideos():
    searchText = request.args.get('searchText')
    myquery =  { "$text" : { "$search" : searchText }} if searchText else None
    video_list = list(db.find(myquery).max_time_ms(10000))
    if not video_list:
        return Response(json_util.dumps({}),mimetype='application/json')

    for video in video_list:
        video.pop('_id')
        videoLink = video.pop('videoId')
        video['videoLink'] = "https://www.youtube.com/watch?v=" + videoLink
    return Response(
        json_util.dumps({'videos': video_list}),
        mimetype='application/json'
    )

# API to trigger the daemon to start fetching the video data from Google API and store it in mongo db.
# Please refer https://ahrefs.com/blog/top-youtube-searches/ for the list of youtube searches we are storing in the database.
# These videos are searched one by one in a cyclic manner.
@app.route("/fetch/start", methods=['POST'])
def startDaemon():
    Thread(target=startYouSearchDaemon).start()
    return Response({})

def startYouSearchDaemon():
    thread = YouSearchDaemon()
    thread.daemon = True
    thread.start(10)

# API to stop the daemon.
@app.route("/fetch/stop", methods=['POST'])
def stopDaemon():
    YouSearchDaemon.stopDaemon()
    return Response({})

if __name__ == "__main__":
    app.run(host ='0.0.0.0', port = 5000, debug = True)