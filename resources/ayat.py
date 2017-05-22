from flask_restful import Resource, reqparse
from flask_jwt import JWT, jwt_required, current_identity
from models.ayat import AyatModel


class Ayat(Resource):
    parser = reqparse.RequestParser()

    parser.add_argument('surah',
        type=str,
        required=True,
        help="Surah argument cannot be left blank!"
    )

    parser.add_argument('number',
        type=int,
        required=True,
        help="Surah number cannot be left blank!"
    )

    parser.add_argument('theme',
        type=str,
        required=False,
        help="This field is for you to describe the theme of the ayat"
    )

    parser.add_argument('note',
        type=str,
        required=False,
        help="This field is for you to input notes for the ayat"
    )

    parser.add_argument('date_refreshed',
        type=lambda x: datetime.strptime(x,'%Y-%m-%dT%H'),
        required=False,
        help="This field is to specify the last time this ayat was refreshed"
    )

    parser.add_argument('difficulty',
        type=int,
        required=False,
        help="This field is for you to specify ayat's difficulty, range 0-5, from easiest to hardest"
    )






    # parser.add_argument('price',
    #     type=float,
    #     required=True,
    #     help="This field cannot be left blank!"
    # )

    # parser.add_argument('price',
    #     type=float,
    #     required=True,
    #     help="This field cannot be left blank!"
    # )
    # parser.add_argument('store_id',
    #     type=int,
    #     required=True,
    #     help="Every item needs a store_id."
    # )

    @jwt_required()
    def get(self):
        data = Ayat.parser.parse_args()
        print("surah is {} and number is {}".format(data.get('surah'),data.get('number')))
        ayat = AyatModel.find_by_surah_number(data.get('surah'), data.get('number'))

        if ayat:
            return ayat.json()
        return {'message': 'Ayat not found'}, 404

    @jwt_required()
    def post(self):
        data = Ayat.parser.parse_args()

        if AyatModel.find_by_surah_number(data.get('surah'), data.get('number')):
            return {'message': "This ayat is already in database."}, 400

        if not AyatModel.surah_exist(data.get('surah')):
            return {'message': "Surah is not valid"}, 400

        ayat = AyatModel(str(current_identity.id), data.get('surah'),
            data.get('number'),
            data.get('date_refreshed'),
            data.get('difficulty'),
            data.get('theme'),
            data.get('note')
            )

        try:
            ayat.save_to_db()
        except:
            return {"message": "An error occurred inserting the ayat."}, 500

        return ayat.json(), 201


        # if ItemModel.find_by_name(name):
        #     return {'message': "An item with name '{}' already exists.".format(name)}, 400

        # data = Item.parser.parse_args()

        # item = ItemModel(name, data['price'], data['store_id'])

        # try:
        #     item.save_to_db()
        # except:
        #     return {"message": "An error occurred inserting the item."}, 500

        # return item.json(), 201

    def delete(self):
        data = Ayat.parser.parse_args()
        # TODO: delete by using filter
        ayat = AyatModel.find_by_surah_number(data.get('surah'), data.get('number'))
        if ayat:
            ayat.delete_from_db()
            return {'message': 'Ayat deleted'}
        return {'message': 'Ayat not found'}, 400

    def put(self):
        data = Ayat.parser.parse_args()
        ayat = AyatModel.find_by_surah_number(data.get('surah'), data.get('number'))


        if ayat:
            ayat.surah = data.get('surah')
            ayat.number = data.get('number')
            ayat.last_refreshed = data.get('date_refreshed')
            ayat.hifz_strength = data.get('hifz_strength')
            ayat.theme = data.get('theme')
            ayat.note  = data.get('note')
        else:
            ayat = AyatModel(str(current_identity.id), data.get('surah'),
                data.get('number'),
                data.get('date_refreshed'),
                data.get('difficulty'),
                data.get('theme'),
                data.get('note')
                )


        ayat.save_to_db()

        return ayat.json()


class AyatGroup(Resource):
    @jwt_required()
    def get(self):
        return {'ayats': list(map(lambda x: x.json(), AyatModel.query.filter_by(ownerID=str(current_identity.id)  )))  }
