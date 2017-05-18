from flask_restful import Resource, reqparse
from flask_jwt import jwt_required
from models.ayat import AyatModel

class Ayat(Resource):
    parser = reqparse.RequestParser()

    parser.add_argument('surah',
        type=str,
        required=True,
        help="This surah cannot be left blank!"
    )

    parser.add_argument('number',
        type=int,
        required=True,
        help="This number cannot be left blank!"
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

    # @jwt_required()
    def get(self):
        ayat = AyatModel.find_by_surah_number(data.get('surah'), data.get('number'))

        if ayat:
            return ayat.json()
        return {'message': 'Ayat not found'}, 404

        # item = ItemModel.find_by_name(name)
        # if item:
        #     return item.json()
        # return {'message': 'Item not found'}, 404

    def post(self):
        data = Ayat.parser.parse_args()

        if AyatModel.find_by_surah_number(data.get('surah'), data.get('number')):
            return {'message': "This ayat is already in database."}, 400

        ayat = AyatModel(data.get('surah'),
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

    def delete(self, name):
        item = ItemModel.find_by_name(name)
        if item:
            item.delete_from_db()

        return {'message': 'Item deleted'}

    def put(self, name):
        data = Ayat.parser.parse_args()

        item = ItemModel.find_by_name(name)

        if item:
            item.price = data['price']
        else:
            item = ItemModel(name, data['price'])

        item.save_to_db()

        return item.json()



        data = Item.parser.parse_args()

        item = ItemModel.find_by_name(name)

        if item:
            item.price = data['price']
        else:
            item = ItemModel(name, data['price'])

        item.save_to_db()

        return item.json()

class AyatGroup(Resource):
    def get(self):
        return {'ayats': list(map(lambda x: x.json(), AyatModel.query.all()))}
