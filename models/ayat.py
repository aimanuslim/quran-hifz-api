from db import db
import difflib
import pdb

class AyatModel(db.Model):
    __tablename__ = 'ayats'

    id = db.Column(db.Integer, primary_key=True)
    surah = db.Column(db.String(80))
    juz = db.Column(db.Integer)
    number = db.Column(db.Integer)
    revisit_frequency = db.Column(db.Integer)
    last_refreshed = db.Column(db.DateTime)
    hifz_strength = db.Column(db.Integer)
    note = db.Column(db.Text)
    theme = db.Column(db.Text)
    ownerID = db.Column(db.Integer)



    # name = db.Column(db.String(80))
    # price = db.Column(db.Float(precision=2))

    # store_id = db.Column(db.Integer, db.ForeignKey('stores.id'))
    # store = db.relationship('StoreModel')

    def __init__(self, ownerID, surah, number, date_refreshed, hifz_strength, theme, note):
        self.ownerID = ownerID
        self.surah = surah
        self.number = number
        # self.juz = self.lookup_juz(surah, number)

        self.revisit_frequency = 0
        self.last_refreshed = date_refreshed
        self.hifz_strength = hifz_strength
        self.theme = theme
        self.note = note


    def json(self):
        return {'owner': self.ownerID, 'surah': self.surah, 'juz': self.juz, 'number': self.number, 'revisit_frequency': self.revisit_frequency, 'last_refreshed': self.last_refreshed, 'hifz_strength': self.hifz_strength, 'theme': self.theme, 'note': self.note}

    # @classmethod
    # def find_by_name(cls, ownerID, name):
    #     # return cls.query.filter_by(name=name).first()
    #     ayat_list = AyatModel.query.filter_by(ownerID=str(current_identity.id)

    @classmethod
    def find_by_surah_number(cls, ownerID, surah, number):
        # return cls.query.filter_by(surah=surah, number=number).first()
        ayat_list = cls.query.filter_by(ownerID=ownerID)
        for ayat in ayat_list:
            if difflib.SequenceMatcher(None, ayat.surah, surah).ratio() > 0.5 and ayat.number == number:
                return ayat
        return None


    @classmethod
    def surah_exist(cls, surah):
        from common.quran_data import surah_list

        # return surah in surah_list
        similar_surah_name = difflib.get_close_matches(surah, surah_list)
        surah_name_found = similar_surah_name[0]

        print('Ratio: '+ str(difflib.SequenceMatcher(None, surah_name_found, surah).ratio()) )
        print("Surah: {} Surah_found: {}".format(surah, surah_name_found) )
        return (difflib.SequenceMatcher(None, surah_name_found, surah).ratio() > 0.5)

    @classmethod
    def ayat_in_range(cls, surah, ayat_number):
        from common.quran_data import filtered_surah_data, surah_list

        ayat_number = int(ayat_number)
        similar_surah_name = difflib.get_close_matches(surah, surah_list)
        surah_name_found = similar_surah_name[0]

        surahs_total_ayat = None
        for surah_info_dict in filtered_surah_data:
            if surah_info_dict.get('englishName') == surah_name_found:
                print("Surah found, number of ayat {}".format(surah_info_dict.get('numberOfAyahs')))
                surahs_total_ayat = surah_info_dict.get('numberOfAyahs')
        if surahs_total_ayat:
            return ayat_number <= surahs_total_ayat
        else:
            print("Surah name {} unfound!".format(surah))
            return False

    @classmethod
    def get_surah_ayat_count(cls, surah):
        from common.quran_data import filtered_surah_data, surah_list


        similar_surah_name = difflib.get_close_matches(surah, surah_list)
        surah_name_found = similar_surah_name[0]

        surahs_total_ayat = None
        for surah_info_dict in filtered_surah_data:
            if surah_info_dict.get('englishName') == surah_name_found:
                print("Surah found, number of ayat {}".format(surah_info_dict.get('numberOfAyahs')))
                surahs_total_ayat = surah_info_dict.get('numberOfAyahs')
        if surahs_total_ayat:
            return surahs_total_ayat
        else:
            print("Surah name {} unfound!".format(surah))
            return False




    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()
