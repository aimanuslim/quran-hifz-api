from flask import Flask
from flask_restful import Api
from flask_jwt import JWT

from security import authenticate, identity
from resources.user import UserRegister
from resources.item import Item, ItemList
from resources.store import Store
from resources.ayat import Ayat
from resources.ayat import AyatGroup
from resources.bot import Bot
from common.quran_data import populate_surah_data


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'jose'
api = Api(app)

@app.before_first_request
def create_tables():
    db.create_all()

@app.before_first_request
def intialize_quran_data():
    populate_surah_data()

jwt = JWT(app, authenticate, identity)  # /auth

api.add_resource(Ayat, '/ayat')
api.add_resource(AyatGroup, '/ayats')
api.add_resource(UserRegister, '/register')

if __name__ == '__main__':
    from db import db
    db.init_app(app)
    app.run(port=5000, debug=True)
