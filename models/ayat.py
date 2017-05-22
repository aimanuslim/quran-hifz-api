from db import db


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

    @classmethod
    def find_by_name(cls, name):
        return cls.query.filter_by(name=name).first()
    @classmethod
    def find_by_surah_number(cls, surah, number):
        return cls.query.filter_by(surah=surah, number=number).first()


    @classmethod
    def surah_exist(cls, surah):
        from common.quran_data import surah_list
        print(surah_list)
        return surah in surah_list

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()
