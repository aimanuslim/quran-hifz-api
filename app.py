from flask import Flask
from flask_restful import Api
from flask_jwt import JWT

from security import authenticate, identity
from resources.user import UserRegister
from resources.hifz import Hifz, HifzRecommendation
from common.utilities import PopulateSurahData, PopulateJuzData


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
    PopulateSurahData()
    PopulateJuzData()


jwt = JWT(app, authenticate, identity)  # /auth

api.add_resource(Hifz, '/hifz')
api.add_resource(UserRegister, '/register')
api.add_resource(HifzRecommendation, '/random')

def create_test_app():
	app = Flask(__name__)
	app.config['TESTING'] = True
	app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
	app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///test.db'
	app.secret_key = 'ian'

	api = Api(app)
	jwt = JWT(app, authenticate, identity)  # /auth
	api.add_resource(Hifz, '/hifz')
	api.add_resource(UserRegister, '/register')
	api.add_resource(HifzRecommendation, '/random')
	return app

if __name__ == '__main__':
    from db import db
    db.init_app(app)
    app.run(port=5000, debug=True)
