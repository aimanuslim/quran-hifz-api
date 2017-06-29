import requests
import nose.tools

def setup():
	url = 'http://127.0.0.1:5000/auth'
	r = requests.get(url)
	if not r: exit("Error sending auth")
	if r.status_code == 401:
		url = 'http://127.0.0.1:5000/register'
		data = {"username":"aiman", "password":"chan"}
		r = requests.get(url, data=data)
		assert r.status_code == 201
	json = json.loads(r.text)
	assert json.get("access_token") != None



