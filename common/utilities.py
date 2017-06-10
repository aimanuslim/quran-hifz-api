import requests
import json


ayatcts_in_surah = dict()
surah_names = dict()
surah_limits_in_all_juz = None

surah_list = []

def PopulateSurahData():
    # url = 'http://api.alquran.cloud/surah'
    # r = requests.get(url)
    # if r:
    with open('common/surahs.json', encoding="utf8") as data_file:
        data = json.load(data_file)
        surah_data = data.get('data')
        # print(surah_data)

        keys = ['englishName', 'numberOfAyahs']

        global ayatcts_in_surah
        global surah_names
        for surah in surah_data:
            ayatcts_in_surah[surah['number']] = surah['numberOfAyahs']
            surah_names[surah['number']] = surah['englishName']

        # ayatcts_in_surah = [{k:v  for k,v in surah.items() if k == 'number' or k == 'numberOfAyahs'} for surah in surah_data]

        # global  surah_list
        # surah_list = [surah.get('englishName').replace("Al", "", 1).replace("-","") for surah in surah_data]

        # ayatcts_in_surah = [{b:c for b,c in a.items() if b == 'a' or b == 't'} for a in k]

        # ayatcts_in_surah = [dict(k,v) for k, v in surah_data]
        # dict((k, surah_data[k]) for k in keys if k in surah_data)

def PopulateJuzData():
    with open('common/juzs.json', encoding="utf8") as data_file:
        data = json.load(data_file)
        global surah_limits_in_all_juz
        surah_limits_in_all_juz = data.get('data')


def isSurahValid(surah):
    return surah < 115 or surah > 0
    

def AyatIsInRange(surahnumber, ayat_number):
    ayat_number = int(ayat_number)
    print("max: {} an: {}".format(ayatcts_in_surah[surahnumber], ayat_number))
    if ayat_number < 0 or ayat_number > ayatcts_in_surah[surahnumber]:
        return False
    return True
    

def FindAyatCountIn(surahnumber):
    return ayatcts_in_surah[surahnumber]
    

def FindJuzGivenSurahAndAyat(surah, ayat):
    global surah_limits_in_all_juz
    if surah_limits_in_all_juz:
        for juz_number, juz_limits in enumerate(surah_limits_in_all_juz):
            
            for sn, an_limits in juz_limits.items():
                # print("AN limits: {} SN: {} surah: {} ayat {}".format(an_limits, sn, surah, ayat))
                if int(sn) == surah and ayat >= an_limits[0] and ayat <= an_limits[1]:
                    return juz_number + 1
    return -1



def JuzInRange(juz):
    return (juz > 0 and juz <= 30)



def FindSurahWithAyatInJuz(juz):
    url = 'http://api.alquran.cloud/juz/' + str(juz)
    r = requests.get(url)
    if r:
        data = json.loads(r.text)
        data = data.get('data')
        surah_numbers = data.get('surahs').keys()
        first_ayat_numberinsurah = data.get('ayahs')[0].get('numberInSurah')
        first_ayat_surahnumber = data.get('ayahs')[0].get('surah').get('number')
        last_ayat_numberinsurah = data.get('ayahs')[-1].get('numberInSurah')
        last_ayat_surahnumber = data.get('ayahs')[-1].get('surah').get('number')

        surah_metadata = dict()
        if first_ayat_surahnumber != last_ayat_surahnumber:
            surah_metadata[first_ayat_surahnumber] = (first_ayat_numberinsurah, ayatcts_in_surah[first_ayat_surahnumber])
            for sn in range(first_ayat_surahnumber + 1, last_ayat_surahnumber):
                surah_metadata[sn] = (1, ayatcts_in_surah[sn])
            surah_metadata[last_ayat_surahnumber] = (1, last_ayat_numberinsurah)
        else:
            surah_metadata[first_ayat_surahnumber] = (first_ayat_numberinsurah, last_ayat_numberinsurah)

        return surah_metadata
    return None


if __name__ == '__main__':
    pass
