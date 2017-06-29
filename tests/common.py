import requests
from requests_jwt import JWTAuth
import json

base_url = 'http://127.0.0.1:5000'
username = 'aiman'
password = 'chan'


def auth():
	auth_url = base_url + '/auth'
	data = {"username": username, "password":password}
	r = requests.post(auth_url, json=data)
	# if not r: exit("Error sending auth")
	if not r: 
	# if r.status_code == 401:
		url = base_url + '/register'
		r = requests.post(url, json=data)
		assert r.status_code == 201, "Status code is {}".format(r.status_code)
		print("User registered!")
		r = requests.post(auth_url, json=data)

	json_data = json.loads(r.text)
	assert json_data.get("access_token") != None, "json_data is  {}".format(json_data)
	return json_data.get("access_token").rstrip()

def post_surah(token, surah):
	url = base_url + '/hifz'
	data = { "surah" : surah }
	auth = JWTAuth(token)
	r = requests.post(url, json=data, headers={'Authorization': 'JWT ' + token})
	assert r.status_code == 201, "Status code is {} token {}".format(r.status_code, token)
	return json.loads(r.text)

def post_ayat(token, surah, ayat):
	url = base_url + '/hifz'
	data = { "surah" : surah , "ayatnumber" : ayat}
	auth = JWTAuth(token)
	r = requests.post(url, json=data, headers={'Authorization': 'JWT ' + token})
	json_response = json.loads(r.text)
	assert r.status_code == 201, "Status code is {} message {}".format(r.status_code, json_response.get('message'))
	return 

def post_ayat_range(token, surah, start, end):
	url = base_url + '/hifz'
	data = {
	  "surah": surah,
	  "ayatnumber": {
	    "start":start,
	    "end":end
	  }
	}
	auth = JWTAuth(token)
	r = requests.post(url, json=data, headers={'Authorization': 'JWT ' + token})
	assert r.status_code == 201, "Status code is {}".format(r.status_code)
	return json.loads(r.text)

def post_juz(token, juz):
	url = base_url + '/hifz'
	data = { "juz" : juz}
	auth = JWTAuth(token)
	r = requests.post(url, json=data, headers={'Authorization': 'JWT ' + token})
	assert r.status_code == 201, "Status code is {}".format(r.status_code)
	return json.loads(r.text)

def get_surah(token, surah):
	url = base_url + '/hifz?surah=' + str(surah)
	auth = JWTAuth(token)
	r = requests.get(url, headers={'Authorization': 'JWT ' + token})
	assert r.status_code == 200, "Status code is {}".format(r.status_code)
	return json.loads(r.text)

def get_ayat(token, surah, ayat):
	url = base_url + '/hifz?surah=' + str(surah) + '&ayat=' + str(ayat)
	auth = JWTAuth(token)
	r = requests.get(url, headers={'Authorization': 'JWT ' + token})
	assert r.status_code == 200, "Status code is {}".format(r.status_code)
	return json.loads(r.text)

def get_juz(token, juz):
	url = base_url + '/hifz?juz=' + str(juz)
	auth = JWTAuth(token)
	r = requests.get(url, headers={'Authorization': 'JWT ' + token})
	assert r.status_code == 200, "Status code is {}".format(r.status_code)
	return json.loads(r.text)

def get_all(token):
	url = base_url + '/hifz' 
	auth = JWTAuth(token)
	r = requests.get(url, headers={'Authorization': 'JWT ' + token})
	assert r.status_code == 200, "Status code is {}".format(r.status_code)
	return json.loads(r.text)	

