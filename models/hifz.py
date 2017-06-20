from db import db
import difflib
import pdb
import requests
import json
from common.utilities import FindJuzGivenSurahAndAyat

class HifzModel(db.Model):
    __tablename__ = 'hifz'

    id = db.Column(db.Integer, primary_key=True)
    surah = db.Column(db.Integer)
    juz = db.Column(db.Integer)
    ayatnumber = db.Column(db.Integer)
    revisit_frequency = db.Column(db.Integer)
    last_refreshed = db.Column(db.DateTime)
    difficulty = db.Column(db.Integer)
    note = db.Column(db.Text)
    theme = db.Column(db.Text)
    ownerID = db.Column(db.Integer)
    group = db.Column(db.Integer)

    def __init__(self, ownerID, surah, ayatnumber):
        self.ownerID = ownerID
        self.surah = surah
        self.ayatnumber = ayatnumber
        self.juz = FindJuzGivenSurahAndAyat(surah, ayatnumber)
        self.revisit_frequency = 0
     


    def json(self):
        return {'owner': self.ownerID, 'surah': self.surah, 'juz': self.juz, 'ayat number': self.ayatnumber, 'revisit_frequency': self.revisit_frequency, 'last_refreshed': self.last_refreshed, 'difficulty': self.difficulty, 'theme': self.theme, 'note': self.note, 'group': self.group}

    @classmethod
    def FindHifzBySurahAndNumber(cls, ownerID, surah, number):
        ayat_exist = cls.query.filter_by(ownerID=ownerID, surah=surah, ayatnumber=number).first()
        return ayat_exist

    def FindByRange(ownerID, surah, start, end):
        return db.session.query(HifzModel).\
        filter( HifzModel.ownerID==ownerID).\
        filter( HifzModel.surah==surah).\
        filter( HifzModel.ayatnumber <= end ).\
        filter( HifzModel.ayatnumber >= start )


    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()
