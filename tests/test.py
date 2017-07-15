from tests.common import *
# from nose.tools import assert_equal, assert_not_equal, assert_raises, raises
from random import sample, randint
from common.utilities import PopulateJuzData, PopulateSurahData
from models.user import UserModel


import app
import copy
import unittest
import tempfile
import os
from db import db
import pdb

hifz_parameters = [
	"theme",
	"date_refreshed",
	"group",
	"difficulty",
	"note",
	"just_refreshed"
]

data_surah_invalid = { "surah" : 123 }
data_surah_valid = { "surah" : 7 }
data_ayat_invalid = {"surah": 66, "ayatnumber": 7000}
data_ayat_range_invalid = {
		"surah": 15, 
		"ayatnumber": 
			{"start": 4,
			"end": 190}
		}
data_ayat_range_valid = {
		"surah": 15, 
		"ayatnumber": 
			{"start": 4,
			"end": 37}
		}
data_nonexistant_range = {
		"surah": 15, 
		"ayatnumber": 
			{"start": 4,
			"end": 39}
		}		
data_juz_valid = { "juz" : 20}
data_juz_invalid = { "juz" : 50 }
data_missing_params = {
	"surah": 15, 
	"ayatnumber": 
		{"start": 4}
	}
data_ayat_valid = {"surah": 65, "ayatnumber": 10}
data_nonexistant = {"surah": 65, "ayatnumber": 2}
data_already_exists = {"surah": 64, "ayatnumber": 13}
data_surah_wparams = {"surah": 3}
data_juz_wparams = {"juz": 30}


class test_main(unittest.TestCase):
	print("Running tests..")
	ayt_cts = PopulateSurahData()
	surah_limits = PopulateJuzData()
	usersDetails = [{
		"username" : "aiman",
		"password" : "chan",
		"token" : ""
	}, 
	{
		"username" : "dummy",
		"password" : "chan",
		"token" : ""
	}]

	


	@classmethod
	def setUpClass(cls):
		cls.app = app.create_test_app()
		db.init_app(cls.app)
		with cls.app.app_context():
			for userDetail in cls.usersDetails:
				db.create_all()
				db.session.add(UserModel(userDetail["username"], userDetail["password"]))
				db.session.commit()
		with cls.app.test_client() as c:
			for i in range(0, len(cls.usersDetails)):
				res = c.post('/auth', data=json.dumps({"username": cls.usersDetails[i].get("username"), "password": cls.usersDetails[i].get("password")}),  content_type='application/json')
				json_data = json.loads(res.get_data(as_text=True))
				cls.usersDetails[i]["token"] = json_data.get('access_token')

	def test_Flow1(self):
		# post operations
		self.post_ayat(data_ayat_valid)
		self.post_range_ayat(data_ayat_range_valid)
		self.post_surah(data_surah_valid)
		self.post_juz(data_juz_valid)
		self.post_hifz_wparams(data_surah_wparams, "surah")
		self.post_hifz_wparams(data_juz_wparams, "juz")

		self.post_ayat_invalid(data_ayat_invalid)
		self.post_range_ayat_invalid(data_ayat_range_invalid)
		self.post_surah_invalid(data_surah_invalid)
		self.post_juz_invalid(data_juz_invalid)
		self.post_ayat_range_missing_params(data_missing_params)
		self.post_ayat_already_exist(data_already_exists)
		self.get()

		# put operations
		self.put_ayat(data_ayat_valid)
		self.put_range_ayat(data_ayat_range_valid)
		self.put_surah(data_surah_valid)
		self.put_juz(data_juz_valid)
		self.put_hifz_wparams(data_surah_wparams, "surah")
		self.put_hifz_wparams(data_juz_wparams, "juz")

		self.put_ayat_invalid(data_ayat_invalid)
		self.put_range_ayat_invalid(data_ayat_range_invalid)
		self.put_surah_invalid(data_surah_invalid)
		self.put_juz_invalid(data_juz_invalid)
		self.put_ayat_range_missing_params(data_missing_params)
		self.put_ayat_already_exist(data_already_exists)


		# delete invalid first
		self.del_nonexistant_ayat(data_nonexistant)
		self.del_nonexistant_range_ayat(data_nonexistant_range)
		self.del_ayat_invalid(data_ayat_invalid)
		self.del_range_ayat_invalid(data_ayat_range_invalid)
		self.del_surah_invalid(data_surah_invalid)
		self.del_juz_invalid(data_juz_invalid)
		self.del_ayat_range_missing_params(data_missing_params)

		# delete existing ayat
		self.del_ayat(data_ayat_valid)
		self.del_range_ayat(data_ayat_range_valid)
		self.del_surah(data_surah_valid)
		self.del_juz(data_juz_valid)
		self.put_hifz_wparams(data_surah_wparams, "surah")
		self.put_hifz_wparams(data_juz_wparams, "juz")

		

	def put_surah_invalid(self, data):
		
		with self.app.test_client() as c:
			for userDetail in self.usersDetails:
				res = c.put('/hifz', data=json.dumps(data), content_type='application/json', headers={'Authorization': 'JWT ' + userDetail.get("token")})
				assert res.status_code == 400, "status: {} msg: {}".format(res.status_code, json_data.get('message'))

		print("Updating invalid surah test PASSED")

	def put_ayat_invalid(self, data):
		with self.app.test_client() as c:
			for userDetail in self.usersDetails:
				res = c.put('/hifz', data=json.dumps(data), content_type='application/json', headers={'Authorization': 'JWT ' + userDetail.get("token")})
				json_data = json.loads(res.get_data(as_text=True))
				assert res.status_code == 400, "status: {} msg: {}".format(res.status_code, json_data.get('message'))
		print("Updating invalid single ayat test PASSED")

	def put_range_ayat_invalid(self, data):
	
		with self.app.test_client() as c:
			for userDetail in self.usersDetails:
				res = c.put('/hifz', data=json.dumps(data), content_type='application/json', headers={'Authorization': 'JWT ' + userDetail.get("token")})
				json_data = json.loads(res.get_data(as_text=True))
				assert res.status_code == 400, "status: {} msg: {}".format(res.status_code, json_data.get('message'))
			
		print("Updating invalid ayat range test PASSED")		


	def put_surah(self, data):
		with self.app.test_client() as c:
			for userDetail in self.usersDetails:
				res = c.put('/hifz', data=json.dumps(data), content_type='application/json', headers={'Authorization': 'JWT ' + userDetail.get("token")})
				assert res.status_code == 200, "status: {} msg: {}".format(res.status_code, json_data.get('message'))
				json_data = json.loads(res.get_data(as_text=True))

				# check total stored ayats
				assert len(json_data.get('ayats')) == self.ayt_cts[json_data.get('surah')]

		print("Updating surah test PASSED")



	def put_juz(self, data):
		with self.app.test_client() as c:
			for userDetail in self.usersDetails:
				res = c.put('/hifz', data=json.dumps(data), content_type='application/json', headers={'Authorization': 'JWT ' + userDetail.get("token")})		
				json_data = json.loads(res.get_data(as_text=True))
				assert res.status_code == 200, "status: {} msg: {}".format(res.status_code, json_data.get('message'))
				ayat_json = json_data.get('ayats')
				last_ayat = json_data.get('ayats')[-1]
				first_ayat = json_data.get('ayats')[0]

				juz_limits = self.surah_limits[data.get('juz') - 1] 
				first_surah_in_juz = min(int(k) for k in juz_limits.keys())
				last_surah_in_juz = max(int(k) for k in juz_limits.keys())

				# check first surah in the juz
				assert first_ayat.get('surah') == first_surah_in_juz
				#check last surah in the juz
				assert last_ayat.get('surah') == last_surah_in_juz
				# check first ayat number within the first surah inn the juz
				assert first_ayat.get('ayatnumber') == juz_limits.get(str(first_surah_in_juz))[0]
				# check the last ayat number within the last surah in the juz
				assert last_ayat.get('ayatnumber') == juz_limits.get(str(last_surah_in_juz))[-1]

		print("Updating juz test PASSED")

	def put_juz_invalid(self, data):
		with self.app.test_client() as c:
			for userDetail in self.usersDetails:
				res = c.put('/hifz', data=json.dumps(data), content_type='application/json', headers={'Authorization': 'JWT ' + userDetail.get("token")})
				json_data = json.loads(res.get_data(as_text=True))
				assert res.status_code == 400, "status: {} msg: {}".format(res.status_code, json_data.get('message'))
		print("Updating invalid juz test PASSED")

	def put_ayat_range_missing_params(self,data):
		
		with self.app.test_client() as c:
			for userDetail in self.usersDetails:
				res = c.put('/hifz', data=json.dumps(data), content_type='application/json', headers={'Authorization': 'JWT ' + userDetail.get("token")})
				assert res.status_code == 400, "status: {} msg: {}".format(res.status_code, json_data.get('message'))
		print("Updating missing params for ayat range test PASSED")


	def put_ayat(self, data):
		with self.app.test_client() as c:
			for userDetail in self.usersDetails:
				res = c.put('/hifz', data=json.dumps(data), content_type='application/json', headers={'Authorization': 'JWT ' + userDetail.get("token")})
				json_data = json.loads(res.get_data(as_text=True))
				assert res.status_code == 200, "status: {} msg: {}".format(res.status_code, json_data.get('message'))
				assert json_data.get("surah") == data.get("surah")
				assert json_data.get("ayatnumber") == data.get("ayatnumber") 			
		print("Updating single ayat test PASSED")

	def put_ayat_already_exist(self, data):
		with self.app.test_client() as c:
			for userDetail in self.usersDetails:
				res = c.put('/hifz', data=json.dumps(data), content_type='application/json', headers={'Authorization': 'JWT ' + userDetail.get("token")})
				res = c.put('/hifz', data=json.dumps(data), content_type='application/json', headers={'Authorization': 'JWT ' + userDetail.get("token")})
				json_data = json.loads(res.get_data(as_text=True))
				assert res.status_code == 200, "status: {} msg: {}".format(res.status_code, json_data.get('message'))
		print("Updating ayat that already exists test PASSED")

	def put_range_ayat(self, data):
		
		with self.app.test_client() as c:
			for userDetail in self.usersDetails:
				res = c.put('/hifz', data=json.dumps(data), content_type='application/json', headers={'Authorization': 'JWT ' + userDetail.get("token")})
				json_data = json.loads(res.get_data(as_text=True))
				# pdb.set_trace()
				assert res.status_code == 200, "status: {} msg: {}".format(res.status_code, json_data.get('message'))
				assert len(json_data.get('ayats')) == (data.get('ayatnumber')["end"] - data.get('ayatnumber')["start"] + 1)
				for ayat in json_data.get('ayats'):
						assert ayat.get("surah") == data.get("surah")

			
		print("Updating ayat range test PASSED")		

	def put_hifz_wparams(self, data, mode):
		new_data = copy.deepcopy(data)
		with self.app.test_client() as c:
			for userDetail in self.usersDetails:
				new_data["theme"] = "new_dummy_theme_" + userDetail.get('username')
				new_data["group"] = "new_dummy_group_" + userDetail.get('username')
				new_data["note"] = "new_dummy_note_" + userDetail.get('username')
				new_data["difficulty"] = 5 
				new_data["date_refreshed"] = "02/07/2017" 

				data["theme"] = "dummy_theme_" + userDetail.get('username')
				data["group"] = "dummy_group_" + userDetail.get('username')
				data["note"] = "dummy_note_" + userDetail.get('username')
				data["difficulty"] = 4
				data["date_refreshed"] = "01/07/2017"
				res = c.put('/hifz', data=json.dumps(new_data), content_type='application/json', headers={'Authorization': 'JWT ' + userDetail.get("token")})
				json_data = json.loads(res.get_data(as_text=True))
				assert res.status_code == 200, "status: {} msg: {}".format(res.status_code, json_data.get('message'))


				# check ayat count within surah
				# pdb.set_trace()
				if mode == "surah" :
					assert len(json_data.get('ayats')) == self.ayt_cts[json_data.get(mode)]
					
				if mode == "juz" :
					juz_limits = self.surah_limits[data.get(mode) - 1]
					total_ayats = 0
					for s, e in juz_limits.values():
						total_ayats += e - s + 1
					assert len(json_data.get('ayats')) == total_ayats, "expected total ayats {} actual {}".format(total_ayats, len(json_data.get('ayats')))

				# pick any ayat within ayats
				hifz_dict = json_data.get('ayats')[randint(1, self.ayt_cts[json_data.get(mode)]) - 1]

				assert hifz_dict.get('theme') != data.get('theme')
				assert hifz_dict.get('group') != data.get('group')
				assert hifz_dict.get('note') != data.get('note')
				assert hifz_dict.get('difficulty') != data.get('difficulty')
				assert hifz_dict.get('date_refreshed') != data.get('date_refreshed')	

				# check params that was specified.
				assert hifz_dict.get("theme") == "new_dummy_theme_" + userDetail.get('username')
				assert hifz_dict.get("note") == "new_dummy_note_" + userDetail.get('username')
				assert hifz_dict.get("group") == "new_dummy_group_" + userDetail.get('username')
				assert hifz_dict.get("difficulty") == 5
				assert hifz_dict.get("last_refreshed") == "02/07/2017"

		print("Updating {} with params test PASSED".format(mode))

	def post_surah_invalid(self, data ):
		
		with self.app.test_client() as c:
			for userDetail in self.usersDetails:
				res = c.post('/hifz', data=json.dumps(data), content_type='application/json', headers={'Authorization': 'JWT ' + userDetail.get("token")})
				assert res.status_code == 400, "status: {} msg: {}".format(res.status_code, json_data.get('message'))

		print("Writing invalid surah test PASSED")

	def post_ayat_invalid(self, data):
		with self.app.test_client() as c:
			for userDetail in self.usersDetails:
				res = c.post('/hifz', data=json.dumps(data), content_type='application/json', headers={'Authorization': 'JWT ' + userDetail.get("token")})
				json_data = json.loads(res.get_data(as_text=True))
				assert res.status_code == 400, "status: {} msg: {}".format(res.status_code, json_data.get('message'))
		print("Writing invalid single ayat test PASSED")

	def post_range_ayat_invalid(self, data):
	
		with self.app.test_client() as c:
			for userDetail in self.usersDetails:
				res = c.post('/hifz', data=json.dumps(data), content_type='application/json', headers={'Authorization': 'JWT ' + userDetail.get("token")})
				json_data = json.loads(res.get_data(as_text=True))
				assert res.status_code == 400, "status: {} msg: {}".format(res.status_code, json_data.get('message'))
			
		print("Writing invalid ayat range test PASSED")		


	def post_surah(self, data):
		with self.app.test_client() as c:
			for userDetail in self.usersDetails:
				res = c.post('/hifz', data=json.dumps(data), content_type='application/json', headers={'Authorization': 'JWT ' + userDetail.get("token")})
				assert res.status_code == 201, "status: {} msg: {}".format(res.status_code, json_data.get('message'))
				json_data = json.loads(res.get_data(as_text=True))

				# check total stored ayats
				assert len(json_data.get('ayats')) == self.ayt_cts[json_data.get('surah')]

		print("Writing surah test PASSED")



	def post_juz(self, data):
		with self.app.test_client() as c:
			for userDetail in self.usersDetails:
				res = c.post('/hifz', data=json.dumps(data), content_type='application/json', headers={'Authorization': 'JWT ' + userDetail.get("token")})		
				json_data = json.loads(res.get_data(as_text=True))
				assert res.status_code == 201, "status: {} msg: {}".format(res.status_code, json_data.get('message'))
				ayat_json = json_data.get('ayats')
				last_ayat = json_data.get('ayats')[-1]
				first_ayat = json_data.get('ayats')[0]

				juz_limits = self.surah_limits[data.get('juz') - 1] 
				first_surah_in_juz = min(int(k) for k in juz_limits.keys())
				last_surah_in_juz = max(int(k) for k in juz_limits.keys())

				# check first surah in the juz
				assert first_ayat.get('surah') == first_surah_in_juz
				#check last surah in the juz
				assert last_ayat.get('surah') == last_surah_in_juz
				# check first ayat number within the first surah inn the juz
				assert first_ayat.get('ayatnumber') == juz_limits.get(str(first_surah_in_juz))[0]
				# check the last ayat number within the last surah in the juz
				assert last_ayat.get('ayatnumber') == juz_limits.get(str(last_surah_in_juz))[-1]

		print("Writing juz test PASSED")

	def post_juz_invalid(self, data):
		with self.app.test_client() as c:
			for userDetail in self.usersDetails:
				res = c.post('/hifz', data=json.dumps(data), content_type='application/json', headers={'Authorization': 'JWT ' + userDetail.get("token")})
				json_data = json.loads(res.get_data(as_text=True))
				assert res.status_code == 400, "status: {} msg: {}".format(res.status_code, json_data.get('message'))
		print("Writing invalid juz test PASSED")

	def post_ayat_range_missing_params(self,data):
		
		with self.app.test_client() as c:
			for userDetail in self.usersDetails:
				res = c.post('/hifz', data=json.dumps(data), content_type='application/json', headers={'Authorization': 'JWT ' + userDetail.get("token")})
				assert res.status_code == 400, "status: {} msg: {}".format(res.status_code, json_data.get('message'))
		print("Writing missing params for ayat range test PASSED")


	def post_ayat(self, data):
		with self.app.test_client() as c:
			for userDetail in self.usersDetails:
				res = c.post('/hifz', data=json.dumps(data), content_type='application/json', headers={'Authorization': 'JWT ' + userDetail.get("token")})
				json_data = json.loads(res.get_data(as_text=True))
				assert res.status_code == 201, "status: {} msg: {}".format(res.status_code, json_data.get('message'))
				assert json_data.get("surah") == data.get("surah")
				assert json_data.get("ayatnumber") == data.get("ayatnumber") 			
		print("Writing single ayat test PASSED")

	def post_ayat_already_exist(self, data):
		with self.app.test_client() as c:
			for userDetail in self.usersDetails:
				res = c.post('/hifz', data=json.dumps(data), content_type='application/json', headers={'Authorization': 'JWT ' + userDetail.get("token")})
				res = c.post('/hifz', data=json.dumps(data), content_type='application/json', headers={'Authorization': 'JWT ' + userDetail.get("token")})
				assert res.status_code == 400, "status: {} msg: {}".format(res.status_code, json_data.get('message'))
		print("Writing ayat that already exists test PASSED")

	def post_range_ayat(self, data):
		
		with self.app.test_client() as c:
			for userDetail in self.usersDetails:
				res = c.post('/hifz', data=json.dumps(data), content_type='application/json', headers={'Authorization': 'JWT ' + userDetail.get("token")})
				json_data = json.loads(res.get_data(as_text=True))
				# pdb.set_trace()
				assert res.status_code == 201, "status: {} msg: {}".format(res.status_code, json_data.get('message'))
				assert len(json_data.get('ayats')) == (data.get('ayatnumber')["end"] - data.get('ayatnumber')["start"] + 1)
				for ayat in json_data.get('ayats'):
						assert ayat.get("surah") == data.get("surah")

			
		print("Writing ayat range test PASSED")		

	def post_hifz_wparams(self, data, mode):
		with self.app.test_client() as c:
			for userDetail in self.usersDetails:
				data["theme"] = "dummy_theme_" + userDetail.get('username')
				data["group"] = "dummy_group_" + userDetail.get('username')
				data["note"] = "dummy_note_" + userDetail.get('username')
				data["difficulty"] = 4 
				data["date_refreshed"] = "01/07/2017" 

				res = c.post('/hifz', data=json.dumps(data), content_type='application/json', headers={'Authorization': 'JWT ' + userDetail.get("token")})
				json_data = json.loads(res.get_data(as_text=True))
				assert res.status_code == 201, "status: {} msg: {}".format(res.status_code, json_data.get('message'))


				# check ayat count within surah
				# pdb.set_trace()
				if mode == "surah" :
					assert len(json_data.get('ayats')) == self.ayt_cts[json_data.get(mode)]
				if mode == "juz" :
					juz_limits = self.surah_limits[data.get(mode) - 1]
					total_ayats = 0
					for s, e in juz_limits.values():
						total_ayats += e - s + 1
					assert len(json_data.get('ayats')) == total_ayats, "expected total ayats {} actual {}".format(total_ayats, len(json_data.get('ayats')))

			

				# assert len(json_data.get('ayats')) == self.ayt_cts[json_data.get(mode)], "output: {} expected {} json_data.get(mode): {} json_data: {}".format(len(json_data.get('ayats')), self.ayt_cts[json_data.get(mode)], json_data.get(mode), json.dumps(json_data, indent=2))
				# pick any ayat within surah
				hifz_dict = json_data.get('ayats')[randint(1, self.ayt_cts[json_data.get(mode)]) - 1]

				# check params that was specified.
				assert hifz_dict.get("theme") == "dummy_theme_" + userDetail.get('username')
				assert hifz_dict.get("note") == "dummy_note_" + userDetail.get('username')
				assert hifz_dict.get("group") == "dummy_group_" + userDetail.get('username')
				assert hifz_dict.get("difficulty") == 4
				assert hifz_dict.get("last_refreshed") == "01/07/2017"

		print("Writing {} with params test PASSED".format(mode))


	def get(self):
		with self.app.test_client() as c:
			for userDetail in self.usersDetails:
				res = c.get('/hifz', headers={'Authorization': 'JWT ' + userDetail.get('token')})
				assert res.status_code == 200, "status: {}".format(res.status_code)

		print("Getting all hifz test PASSED")	

	@classmethod
	def tearDownClass(cls):
		with cls.app.app_context():
			db.drop_all()


if __name__ == '__main__':
    unittest.main()









