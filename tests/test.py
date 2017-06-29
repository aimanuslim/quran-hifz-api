from tests.common import *
from nose.tools import assert_equal, assert_not_equal, assert_raises, raises
import unittest
from random import sample, randint
from common.utilities import PopulateJuzData, PopulateSurahData
import app


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





class test_main(unittest.TestCase):
	print("Running tests..")
	ayt_cts = PopulateSurahData()
	surah_limits = PopulateJuzData()
	token = None

	@classmethod
	def setUpClass(cls):
		cls.token = auth()

	def test_positive_checking(self):
		wr_surah(self.token, 4)
		wr_ayat(self.token, 3, 5)
		wr_juz(self.token, 20)

	def test_negative_checking(self):
		assert_raises(AssertionError, wr_surah, self.token, 144)

		assert_raises(AssertionError, wr_ayat, self.token, 1, 300)

		assert_raises(AssertionError, wr_juz, self.token, 56)
	# for i in range(1, 5):
		
	# 	surah = randint(1, 114)
	# 	wr_surah(token, surah)

	# 	surah = randint(1, 114)
	# 	ayat = randint(1, ayt_cts[surah])
	# 	wr_ayat(token, surah, ayat)

	# 	juz = randint(1, 30)
	# 	wr_juz(token, juz)


	# for i in range(1, 5):
	# 	surah = randint(115, 200)
	# 	assert_raises(AssertionError, wr_surah, token, surah)

	# 	surah = randint(1, 114)
	# 	ayat = randint(ayt_cts[surah] + 1, ayt_cts[surah] + 200)
	# 	assert_raises(AssertionError, wr_ayat, token, surah, ayat)

	# 	juz = randint(31, 60)
	# 	assert_raise(AssertionError, wr_juz, token, juz)



if __name__ == '__main__':
    unittest.main()









