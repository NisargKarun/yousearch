# YouSearch

A simple application to access the latest YouTube videos and their meta data. It asynchronously fetches the metadata of YouTube videos continuously and exposes REST APIs to search videos by keywords.


<B>Steps for local setup:</B> 

1. Clone the repository using the command `git clone https://github.com/NisargKarun/yousearch.git`

2. Build a docker image using the command `docker build  -t yousearch:{tag}  .`

3. Run the docker image using the command `docker run -d -p {localport}:5000 yousearch:{tag}`. Please make sure that the localport passed to this command is not already being used.

4. Get started by hitting the localhost API endpoint `localhost:{localport}/`


<B>API Endpoints:</B> 

1. `/youtube/videos?pageToken={pageToken}&limit={limit}`<br/>
    <i>Description</i>: Fetches the latest YouTube videos stored in the database. Uses keyset pagination to fetch older data.<br/>
    <i>Type</i>: GET<br/>
    <i>Query Parameters</i>:<br/>
    <i>pageToken</i> : The API uses keyset pagination on the published Time field. So the user can provide the pageToken value to fetch the next set of videos. The value                   can be taken from the nextPageToken field provided in the original API response. By default pageToken value is None and the latest videos will be                   fetched.
    <i>limit</i>: Default value is set to 10. If limit is provided, it will be applied to the result set. Maximum value is 10.
    
2. `/youtube/search?searchText={comma,separated,search,text,list}`<br/>
    <i>Description</i>: Fetches the YouTube videos stored in the database whose title or description contains any of the words provided in the search key.<br/>
    <i>Type</i>: GET<br/>
    <i>Query Parameter</i>:<br/>
    <i>searchText</i>: Comma separated search text list. Please dont use it without searchText as pagination is not used here.
    
3.  `/fetch/start`<br/>
    <i>Description</i>: API to trigger the daemon to start fetching the video data from Google API and store it in mongo db. Please refer https://ahrefs.com/blog/top-youtube-searches/ for the list of youtube searches we are storing in the database. These videos are searched one by one in a cyclic manner.<br/>
    <i>Type</i>: POST<br/>
    <i>Note</i>: The same functionality is also provided by the service launch endpoint(http://127.0.0.1:5000/). This is done so that the daemon is started automatically when the service is launched.
    
4.  `/fetch/stop`<br/>
    <i>Description</i>: API to stop the daemon.<br/>
    <i>Type</i>: POST<br/>
    
<B>Mongo DB:</B>

<i>Database name</i>: you_search

<i>Collections</i>

1.  api_keys: Stores the list of API keys used to access Google APIs

2.  queries: Stores the list of queries whose results are to be fetched the daemon

3.  videos: Stores the video metadata information<br><br>
    <i>Indexes used</i>:<br/>
    ```
	{
		"v" : 2,
		"key" : {
			"_id" : 1
		},
		"name" : "_id_"
	},
	{
		"v" : 2,
		"key" : {
			"publishedAt" : -1
		},
		"name" : "publishedAt_-1"
	},
	{
		"v" : 2,
		"key" : {
			"_fts" : "text",
			"_ftsx" : 1
		},
		"name" : "title_text_description_text",
		"background" : true,
		"weights" : {
			"description" : 1,
			"title" : 1
		},
		"default_language" : "english",
		"language_override" : "language",
		"textIndexVersion" : 3
	},
	{
		"v" : 2,
		"unique" : true,
		"key" : {
			"videoId" : 1
		},
		"name" : "videoId_1"
	}
    
    
<B>TODO:</B>

1. Enable authorization using JWT or oauth to regulate access to the APIs.
2. Optimize the daemon functionality to handle cases where the same results are being fetched repeatedly. Use nexPageToken provided by the google API results to fetch older data in this case.
3. Increase security for the storage of mongodb credentials as well as the API tokens using encryption.
4. Add an API endpoint to add new search texts whose results need to be fetched.
    

    
    

