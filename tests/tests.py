from tests.init import setup
from helper import *



def test_surah(surah):
	post_surah(surah)
	get_surah(surah)

def test_juz(juz):
	post_juz(juz)
	get_juz(juz)




@with_setup(setup, None)
def test_main():
	pass