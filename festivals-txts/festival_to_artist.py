import requests

for i in range(2000, 2018):
	with open('rock-am-ring-' + str(i) + '.txt', 'r') as f:
		festival = f.read()
	
	artists = festival.split(',')

	for artist in artists:

		req_string = "https://api.spotify.com/v1/search?q=*" + artist + "*&type=artist" 

		r = requests.get(req_string, auth = ())
		if r.json()['artists']['items']:
			print(r.json()['artists']['items'][0]['id'])
		else:
			print(artist)