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

    @jwt_required()
    def post(self):
        data = Ayat.parser.parse_args()

        if AyatModel.find_by_surah_number(str(current_identity.id), data.get('surah'), data.get('number')):
            return {'message': "This ayat is already in database."}, 400

        if not AyatModel.surah_exist(data.get('surah')):
            return {'message': "Surah is not valid"}, 400

        if  not AyatModel.ayat_in_range(data.get('surah'), data.get('number')):
            return {'message': "Ayat is out of range"}, 400

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


    def delete(self):
        data = Ayat.parser.parse_args()
        # TODO: delete by using filter
        ayat = AyatModel.find_by_surah_number(str(current_identity.id), data.get('surah'), data.get('number'))
        if ayat:
            ayat.delete_from_db()
            return {'message': 'Ayat deleted'}, 200
        return {'message': 'Ayat not found'}, 400

    def put(self):
        data = Ayat.parser.parse_args()
        ayat = AyatModel.find_by_surah_number(str(current_identity.id), data.get('surah'), data.get('number'))

        if ayat:
            ayat.surah = data.get('surah')
            ayat.number = data.get('number')
            ayat.last_refreshed = data.get('date_refreshed')
            ayat.difficulty = data.get('difficulty')
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

        return ayat.json(), 201


class MemorizedAyats(Resource):
    parser = reqparse.RequestParser()

    parser.add_argument('surah',
        type=str,
        required=False,
        help="Parameter to filter by surah"
    )

    parser.add_argument('juz',
        type=str,
        required=False,
        help="Parameter to filter by juz"
    )



    @jwt_required()
    def get(self):
        data = MemorizedAyats.parser.parse_args()

        if data.get('surah'):
            return {'ayats': list(map(lambda x: x.json(), AyatModel.query.filter_by(ownerID=str(current_identity.id), surah=data.get('surah') )))  }, 200

        return {'ayats': list(map(lambda x: x.json(), AyatModel.query.filter_by(ownerID=str(current_identity.id)  )))  }, 200



class Surah(Resource):
    parser = reqparse.RequestParser()

    parser.add_argument('surah',
        type=str,
        required=True,
        help="2: Surah argument cannot be left blank!"
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

    @jwt_required()
    def get(self):
        pass

    def save_ayat(self, ownerID, surah, number, date_refreshed, difficulty, theme, note):
        ayat = AyatModel(ownerID, surah, number, date_refreshed, difficulty, theme, note)
        if not AyatModel.find_by_surah_number(ownerID, surah, number):
            ayat.save_to_db()
        else:
            print('Surah {} ayat {} is already in database.'.format(surah, number))
        return ayat

    @jwt_required()
    def post(self):
        data = Surah.parser.parse_args()
        surahs_list = list()
        surahs_total_ayat_count = 0

        if data.get('surah'):
            surah_data = data.get('surah')
            if isinstance(surah_data, list):
                # list handling
                for surah_name in surah_data:
                        surahs_list.append(surah_name)
                        surah_ayat_count = AyatModel.get_surah_ayat_count(surah_name)
                        surahs_total_ayat_count += surah_ayat_count
                        print('Surah name in list surah {}'.format(surah_name))
                        for ayt_number in range(1, surah_ayat_count + 1):
                            self.save_ayat(str(current_identity.id),
                                surah_name,
                                ayt_number,
                                data.get('date_refreshed'),
                                data.get('difficulty'),
                                data.get('theme'),
                                data.get('note'))
                return {'surah': surahs_list, 'total': surahs_total_ayat_count}, 201
            else:
                # single surah
                surah_name = surah_data
                print('Surah name in single surah {}'.format(surah_name))
                surah_ayat_count = AyatModel.get_surah_ayat_count(surah_name)
                surahs_total_ayat_count += surah_ayat_count
                for ayt_number in range(1, surah_ayat_count + 1):
                    self.save_ayat(str(current_identity.id),
                        surah_name,
                        ayt_number,
                        data.get('date_refreshed'),
                        data.get('difficulty'),
                        data.get('theme'),
                        data.get('note'))
                return {'surah': surah_name, 'total': surahs_total_ayat_count}, 201
        return {'message', 'Surah not specified'}, 400
