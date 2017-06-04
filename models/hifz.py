from db import db
import difflib
import pdb

class HifzModel(db.Model):
    __tablename__ = 'hifz'

    id = db.Column(db.Integer, primary_key=True)
    surah = db.Column(db.Integer)
    juz = db.Column(db.Integer)
    ayatnumber = db.Column(db.Integer)
    revisit_frequency = db.Column(db.Integer)
    last_refreshed = db.Column(db.DateTime)
    hifz_strength = db.Column(db.Integer)
    note = db.Column(db.Text)
    theme = db.Column(db.Text)
    ownerID = db.Column(db.Integer)

    def __init__(self, ownerID, surah, juz, ayatnumber, date_refreshed, hifz_strength, theme, note):
        self.ownerID = ownerID
        self.surah = surah
        self.ayatnumber = ayatnumber
        self.juz = juz
        self.revisit_frequency = 0
        self.last_refreshed = date_refreshed
        self.hifz_strength = hifz_strength
        self.theme = theme
        self.note = note


    def json(self):
        return {'owner': self.ownerID, 'surah': self.surah, 'juz': self.juz, 'number': self.ayatnumber, 'revisit_frequency': self.revisit_frequency, 'last_refreshed': self.last_refreshed, 'hifz_strength': self.hifz_strength, 'theme': self.theme, 'note': self.note}

    @classmethod
    def AlreadyExist(cls, ownerID, surah, number):
        ayat_exist = cls.query.filter_by(ownerID=ownerID, surah=surah, ayatnumber=number)
        return None


    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()
