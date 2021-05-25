from bson import json_util
from flask import Flask, render_template, request, jsonify, Response
from service.YouSearchDaemon import YouSearchDaemon

from threading import Thread
from mongo.Mongo import MongoDB

app = Flask(__name__)

db = MongoDB(database_name='you_search', collection_name='videos')

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

@app.route("/fetch/<int:duration>", methods=['POST'])
def startDaemon(duration):
    thread = YouSearchDaemon()
    thread.daemon = True
    thread.start(10)
    thread.join(1.0)
    return

@app.route("/fetch/stop", methods=['POST'])
def stopDaemon():
    YouSearchDaemon.stopDaemon()
    return

app.run(host ='0.0.0.0', port = 5000, debug = True)