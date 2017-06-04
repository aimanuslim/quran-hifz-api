from flask_restful import Resource, reqparse
from flask_jwt import JWT, jwt_required, current_identity
from models.hifz import HifzModel
from common.utilities import isSurahValid, AyatIsInRange, FindAyatCountIn, FindJuzGivenSurahAndAyat, FindSurahWithAyatInJuz
import json


class Hifz(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('surah',
        type=int,
        required=False,
        help="The surah number that you memorized"
    )

    parser.add_argument('ayatnumber',
        # type=int,
        required=False,
        help="the number of the ayat within the surah"
    )


    parser.add_argument('juz',
        type=int,
        required=False,
        help="the juz number"
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
        data = Hifz.parser.parse_args()
        surahnumber = data.get('surah')
        ayatnumber = data.get('ayatnumber')
        ayatnumber = ayatnumber.replace("\'","\"") # to satisfy json loads requirement, need to replace single quotes with double quotes
        ayatnumber = json.loads(ayatnumber)

        juz = data.get('juz')

        if surahnumber and ayatnumber:
            print("Ayat number parameter: {} {}".format(ayatnumber, type(ayatnumber)))
            if HifzModel.AlreadyExist(str(current_identity.id), surahnumber, ayatnumber):
                return {'message': "This ayat is already in database."}, 400
            if not isSurahValid(surahnumber):
                return {'message': "Surah is not valid"}, 400
            if  isinstance(ayatnumber, dict):
                if not ayatnumber['start'] or not ayatnumber['end']:
                    return {'message': "Invalid ayat limits format"}, 400
                else:
                    if not AyatIsInRange(surahnumber, ayatnumber['start']) or not AyatIsInRange(surahnumber, ayatnumber['end']):
                        return {'message': "Either limit is out of range"}, 400
            if  not AyatIsInRange(surahnumber, ayatnumber):
                return {'message': "Ayat is out of range"}, 400

            # TODO: need to loop over range
            juz = FindJuzGivenSurahAndAyat(surahnumber, ayatnumber)
            hifz = HifzModel(str(current_identity.id),
                surahnumber,
                juz,
                ayatnumber,
                data.get('date_refreshed'),
                data.get('hifz_strength'),
                data.get('theme'),
                data.get('note')
            )
            try:
                hifz.save_to_db()
            except:
                return {"message": "An error occurred inserting the data."}, 500

            return hifz.json(), 201
        if surahnumber and not ayatnumber:
            if not isSurahValid(surahnumber):
                return {'message': "Surah is not valid"}, 400

            ayatct = FindAyatCountIn(surahnumber)
            print("Ayat count: {}".format(ayatct))
            for ayatnumber in range(1, ayatct + 1):
                juz = FindJuzGivenSurahAndAyat(surahnumber, ayatnumber)
                hifz = HifzModel(str(current_identity.id),
                    surahnumber,
                    juz,
                    ayatnumber,
                    data.get('date_refreshed'),
                    data.get('hifz_strength'),
                    data.get('theme'),
                    data.get('note')
                )
                try:
                    hifz.save_to_db()
                except:
                    return {"message": "An error occurred inserting the data."}, 500
            return {'surah': surahnumber, 'total_ayat': ayatct}, 201

        if juz and not surahnumber and not ayatnumber:
            # a list of tuples where each tuple will contain a surah number and its last ayat that is contained within that juz
            limits_dict = FindSurahWithAyatInJuz(juz)
            for (sn,limits) in limits_dict.items():
                for ayatnumber in range(limits[0], limits[1] + 1):
                    hifz = HifzModel(str(current_identity.id),
                        sn,
                        juz,
                        ayatnumber,
                        data.get('date_refreshed'),
                        data.get('hifz_strength'),
                        data.get('theme'),
                        data.get('note')
                    )
                    try:
                        hifz.save_to_db()
                    except:
                        return {"message": "An error occurred inserting the data."}, 500
            # TODO: change the return values later
            return {'juz': juz}, 201
        return {'Some parameters are missing!'}, 400

    def delete(self):
        pass

    def put(self):
        pass


class MemorizedAyats(Resource):
    @jwt_required()
    def get(self):
        return {'ayats': list(map(lambda x: x.json(), HifzModel.query.filter_by(ownerID=str(current_identity.id)  )))  }, 200

class MemorizedAyatsFiltered(MemorizedAyats):
    @jwt_required()
    def get(self, mode, number):
        print("Mode {}".format(mode))
        print("number {}".format(number))

        if not number.isdigit():
            return {'message': "Need to provide {} number".format(mode)}, 400

        if mode == 'surah':

            return {'ayats': list(map(lambda x: x.json(), HifzModel.query.filter_by(ownerID=str(current_identity.id), surah=number )))  }, 200

        if mode == 'juz':
            return {'ayats': list(map(lambda x: x.json(), HifzModel.query.filter_by(ownerID=str(current_identity.id), juz=number )))  }, 200

        return {'message': "Invalid url format"}, 400
