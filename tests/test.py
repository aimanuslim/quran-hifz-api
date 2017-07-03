from tests.common import *
# from nose.tools import assert_equal, assert_not_equal, assert_raises, raises
from random import sample, randint
from common.utilities import PopulateJuzData, PopulateSurahData
from models.user import UserModel


import app
import unittest
import tempfile
import os
from db import db
import pdb



def wr_surah(token, surah):
	post_surah(token, surah)
	hifz_list = get_surah(token, surah).get('ayats')
	assert len(hifz_list) != 0
	for hifz in hifz_list:
		assert hifz.get('surah') == surah, "Check retrieved hifz - surah = {} failed!".format(surah)

def wr_juz(token, juz):
	post_juz(token, juz)
	hifz_list = get_juz(token, juz).get('ayats')
	assert len(hifz_list) != 0
	for hifz in hifz_list:
		assert hifz.get('juz') == juz, "Check retrieved hifz - juz = {} failed!".format(juz)


def wr_ayat(token, surah, ayat):
	post_ayat(token, surah, ayat)
	ayat_list = get_ayat(token, surah, ayat).get('ayats')
	assert len(ayat_list) == 1, "Multiple ayat found when retrieving ayat in surah!"
	ayat_json = ayat_list[0]
	assert ayat_json.get('ayat number') == ayat, "Check retrieved hifz - ayat (within surah) = {} failed!".format(ayat)
	assert ayat_json.get('surah') == surah, "Check retrieved hifz - surah (for ayat) = {} failed!".format(surah)




hifz_parameters = [
	"theme",
	"date_refreshed",
	"group",
	"difficulty",
	"note",
	"just_refreshed"
]


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


	def test_wr_surah(self):
		# pdb.set_trace()
		
		with self.app.test_client() as c:
			for userDetail in self.usersDetails:
				data = { "surah" : randint(1, 114) }
				res = c.post('/hifz', data=json.dumps(data), content_type='application/json', headers={'Authorization': 'JWT ' + userDetail.get("token")})
				assert res.status_code == 201, "status: {}".format(res.status_code)
				json_data = json.loads(res.get_data(as_text=True))
				assert len(json_data.get('ayats')) == self.ayt_cts[json_data.get('surah')]

	def test_wr_surah_wparams(self):
		with self.app.test_client() as c:
			for userDetail in self.usersDetails:
				data = { "surah" : randint(1, 114) }
				data["theme"] = "dummy_theme" + userDetail.get('username')
				data["group"] = "dummy_group" + userDetail.get('username')
				data["note"] = "dummy_note" + userDetail.get('username')
				data["difficulty"] = 4 
				data["date_refreshed"] = "01/07/2017" 

				res = c.post('/hifz', data=json.dumps(data), content_type='application/json', headers={'Authorization': 'JWT ' + userDetail.get("token")})
				assert res.status_code == 201, "status: {}".format(res.status_code)
				json_data = json.loads(res.get_data(as_text=True))
				assert len(json_data.get('ayats')) == self.ayt_cts[json_data.get('surah')]
				hifz_dict = json_data.get('ayats')[randint(1, self.ayt_cts[json_data.get('surah')])]
				assert hifz_dict.get("theme") == "dummy_theme" + userDetail.get('username')
				assert hifz_dict.get("note") == "dummy_note" + userDetail.get('username')
				assert hifz_dict.get("group") == "dummy_group" + userDetail.get('username')
				assert hifz_dict.get("difficulty") == 4
				assert hifz_dict.get("date_refreshed") == "01/07/2017"


	def test_get(self):
		with self.app.test_client() as c:
			for userDetail in self.usersDetails:
				res = c.get('/hifz', headers={'Authorization': 'JWT ' + userDetail.get('token')})
				assert res.status_code == 200, "status: {}".format(res.status_code)

	@classmethod
	def tearDownClass(cls):
		with cls.app.app_context():
			db.drop_all()


	# def test_positive_checking(self):
	# 	wr_surah(self.token, 4)
	# 	wr_ayat(self.token, 3, 5)
	# 	wr_juz(self.token, 20)

	# def test_negative_checking(self):
	# 	assert_raises(AssertionError, wr_surah, self.token, 144)

	# 	assert_raises(AssertionError, wr_ayat, self.token, 1, 300)

	# 	assert_raises(AssertionError, wr_juz, self.token, 56)




if __name__ == '__main__':
    unittest.main()









