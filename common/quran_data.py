import requests
import json


filtered_surah_data = []
surah_list = []

def populate_surah_data():
    url = 'http://api.alquran.cloud/surah'
    r = requests.get(url)
    if r:
        data = json.loads(r.text)
        surah_data = data.get('data')
        # print(surah_data)

        keys = ['englishName', 'numberOfAyahs']

        global filtered_surah_data
        filtered_surah_data = [{k:v for k,v in surah.items() if k == 'englishName' or k == 'numberOfAyahs'} for surah in surah_data]
        global  surah_list
        surah_list = [surah.get('englishName') for surah in surah_data]

        # filtered_surah_data = [{b:c for b,c in a.items() if b == 'a' or b == 't'} for a in k]

        # filtered_surah_data = [dict(k,v) for k, v in surah_data]
        # dict((k, surah_data[k]) for k in keys if k in surah_data)


if __name__ == '__main__':
    populate_surah_data()
    print(surah_list)
    print(filtered_surah_data)

        # for surah in surah_data:
            # surah_data = [(k: v) for key, value in surah_data.iteritems() if key == 'englishName' or key ==]
