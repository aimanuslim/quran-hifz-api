import requests
import json


ayatcts_in_surah = dict()
surah_names = dict()

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
    for juz_number in range(1, 31):
        url = 'http://api.alquran.cloud/juz/' + str(juz_number)
        r = requests.get(url)
        if r:
            data = json.loads(r.text)

def isSurahValid(surah):
    return surah < 115 or surah > 0
    # # return surah in surah_list
    # similar_surah_name = difflib.get_close_matches(surah, surah_list)
    # surah_name_found = similar_surah_name[0]
    #
    # print('Ratio: '+ str(difflib.SequenceMatcher(None, surah_name_found, surah).ratio()) )
    # print("Surah: {} Surah_found: {}".format(surah, surah_name_found) )
    # return (difflib.SequenceMatcher(None, surah_name_found, surah).ratio() > 0.5)

def AyatIsInRange(surahnumber, ayat_number):
    ayat_number = int(ayat_number)
    if ayat_number < 0 or ayat_number > ayatcts_in_surah[surahnumber]:
        return False
    return True
    # similar_surah_name = difflib.get_close_matches(surah, surah_list)
    # surah_name_found = similar_surah_name[0]
    #
    # surahs_total_ayat = None
    # for surah_info_dict in ayatcts_in_surah:
    #     if surah_info_dict.get('englishName') == surah_name_found:
    #         print("Surah found, number of ayat {}".format(surah_info_dict.get('numberOfAyahs')))
    #         surahs_total_ayat = surah_info_dict.get('numberOfAyahs')
    # if surahs_total_ayat:
    #     return ayat_number <= surahs_total_ayat
    # else:
    #     print("Surah name {} unfound!".format(surah))
    #     return False

def FindAyatCountIn(surahnumber):
    return ayatcts_in_surah[surahnumber]
    #
    # similar_surah_name = difflib.get_close_matches(surah, surah_list)
    # surah_name_found = similar_surah_name[0]
    #
    # surahs_total_ayat = None
    # for surah_info_dict in ayatcts_in_surah:
    #     if surah_info_dict.get('englishName') == surah_name_found:
    #         print("Surah found, number of ayat {}".format(surah_info_dict.get('numberOfAyahs')))
    #         surahs_total_ayat = surah_info_dict.get('numberOfAyahs')
    # if surahs_total_ayat:
    #     return surahs_total_ayat
    # else:
    #     print("Surah name {} unfound!".format(surah))
    #     return False

def FindJuzGivenSurahAndAyat(surah, ayat):
    url = 'http://api.alquran.cloud/ayah/' + str(surah) + ":" + str(ayat)
    r = requests.get(url)
    if r:
        data = json.loads(r.text)
        return data.get('data').get('juz')
    print("Juz not found")
    return None

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
