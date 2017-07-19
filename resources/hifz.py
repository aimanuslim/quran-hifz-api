from flask_restful import Resource, reqparse
from flask_jwt import JWT, jwt_required, current_identity
from models.hifz import HifzModel
from common.utilities import *
import datetime
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

    parser.add_argument('start',
        type=int,
        required=False,
        help="the starting range of ayat"
    )

    parser.add_argument('end',
        type=int,
        required=False,
        help="the ending range of ayat"
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
        type=lambda x: datetime.datetime.strptime(x,'%d/%m/%Y'),
        required=False,
        help="This field is to specify the last time this ayat was refreshed"
    )

    parser.add_argument('difficulty',
        type=int,
        required=False,
        help="This field is for you to specify ayat's difficulty, range 0-5, from easiest to hardest"
    )

    parser.add_argument('group',
        type=str,
        required=False,
        help="This field is for you to specify ayat's group, if you need to chain it with some other similar ayats"
    )

    parser.add_argument('just_revisited',
        type=bool,
        required=False,
        help="This field is to indicate that this ayat was just revisited recently (within one day)"
    )


    @jwt_required()
    def post(self):
        data = Hifz.parser.parse_args()
        surahnumber = data.get('surah')

        ayatnumber = data.get('ayatnumber')
        if ayatnumber and isinstance(ayatnumber, str): 
            ayatnumber = ayatnumber.replace("\'","\"") # to satisfy json loads requirement, need to replace single quotes with double quotes
            ayatnumber = json.loads(ayatnumber)

        juz = data.get('juz')

        if surahnumber and ayatnumber:

            if not isSurahValid(surahnumber):
                return {'message': "Surah is not valid"}, 400

            if  isinstance(ayatnumber, dict):
                # sanity checking
                if not ayatnumber.get('start') or not ayatnumber.get('end'):
                    return {'message': "Invalid ayat limits format"}, 400
                else:
                    if not AyatIsInRange(surahnumber, ayatnumber.get('start')) or not AyatIsInRange(surahnumber, ayatnumber.get('end')):
                        return {'message': "Either limit is out of range"}, 400
                
                # start saving
                saved_array = []
                for an in range(ayatnumber.get('start'), ayatnumber.get('end') + 1):
                    if HifzModel.FindHifzBySurahAndNumber(str(current_identity.id), surahnumber, an): return {'message': "Some of the ayat in range are already in database."}, 400
                    hifz = HifzModel(str(current_identity.id), surahnumber, an)
                    hifz = modify_properties(hifz, data)
                    try:
                        hifz.save_to_db()
                        # print("Saved: {}".format(hifz.json()))
                        saved_array.append(hifz.json());
                    except:
                        return {"message": "An error occurred inserting the data."}, 500
                return {'ayats': saved_array}, 201;
            else:
                # sanity checking
                if HifzModel.FindHifzBySurahAndNumber(str(current_identity.id), surahnumber, ayatnumber):return {'message': "This ayat is already in database."}, 400
                if not AyatIsInRange(surahnumber, ayatnumber): return {'message': "Ayat is out of range"}, 400
                
                # start saving
                hifz = HifzModel(str(current_identity.id), surahnumber, ayatnumber)
                hifz = modify_properties(hifz, data)

                try:
                    hifz.save_to_db()
                except:
                    return {"message": "An error occurred inserting the data."}, 500

                return hifz.json(), 201


        if surahnumber and not ayatnumber:
            if not isSurahValid(surahnumber):
                return {'message': "Surah is not valid"}, 400

            ayatct = FindAyatCountIn(surahnumber)
            saved_array = []
            for an in range(1, ayatct + 1):
                if HifzModel.FindHifzBySurahAndNumber(str(current_identity.id), surahnumber, an): return {'message': "Some ayat in surah already in database."}, 400
                hifz = HifzModel(str(current_identity.id), surahnumber, an)
                hifz = modify_properties(hifz, data)
                try:
                    hifz.save_to_db()
                    saved_array.append(hifz.json())
                except:
                    
                    return {"message": "An error occurred inserting the data."}, 500
            return {'surah': surahnumber, 'ayats': saved_array}, 201

        if juz and not surahnumber and not ayatnumber:

            if not JuzInRange(juz):
                return {"message": "Juz is not valid"}, 400

            # a list of tuples where each tuple will contain a surah number and its last ayat that is contained within that juz
            limits_dict = FindSurahWithAyatInJuz(juz)
            saved_array = []
            for (sn,limits) in limits_dict.items():
                for an in range(limits[0], limits[1] + 1):
                    if HifzModel.FindHifzBySurahAndNumber(str(current_identity.id), sn, an):
                        return {'message': "This juz is already in database."}, 400
                    hifz = HifzModel(str(current_identity.id), sn, an)
                    hifz = modify_properties(hifz, data)
                    try:
                        hifz.save_to_db()
                        saved_array.append(hifz.json())
                    except:
                        return {"message": "An error occurred inserting the data."}, 500
            return {'juz': juz, 'ayats': saved_array}, 201
        return {'Some parameters are missing!'}, 400

    @jwt_required()
    def delete(self):
        data = Hifz.parser.parse_args()
        surahnumber = data.get('surah')
        ayatnumber = data.get('ayatnumber')
        if ayatnumber:
            ayatnumber = ayatnumber.replace("\'","\"") # to satisfy json loads requirement, need to replace single quotes with double quotes
            ayatnumber = json.loads(ayatnumber)

        juz = data.get('juz')

        if surahnumber and ayatnumber:
            if not isSurahValid(surahnumber):
                return {'message': "Surah is not valid"}, 400
            if  isinstance(ayatnumber, dict):
                if not ayatnumber.get('start') or not ayatnumber.get('end'):
                    return {'message': "Invalid ayat limits format"}, 400
                else:
                    if not AyatIsInRange(surahnumber, ayatnumber.get('start')) or not AyatIsInRange(surahnumber, ayatnumber.get('end')):
                        return {'message': "Either limit is out of range"}, 400
                saved_array = []
                for an in range(ayatnumber.get('start'), ayatnumber.get('end') + 1):
                    hifz = HifzModel.FindHifzBySurahAndNumber(str(current_identity.id), surahnumber, an);
                    if not hifz: return {"message": "Some ayat in range does not exist"}, 400
                    try:
                        hifz.delete_from_db();
                    except:
                        return {"message": "An error occurred deleting the data."}, 500
                return {}, 200; 
            else:
                if not AyatIsInRange(surahnumber, ayatnumber):
                    return {'message': "Ayat is out of range"}, 400

                hifz = HifzModel.FindHifzBySurahAndNumber(str(current_identity.id), surahnumber, ayatnumber)
                if not hifz: return {"message": "Ayat not found"}, 400
                try:
                    hifz.delete_from_db()
                except:
                    return {"message": "An error occurred deleting the data."}, 500
                return {}, 200 # success
                



        if surahnumber and not ayatnumber:
            if not isSurahValid(surahnumber):
                return {'message': "Surah is not valid"}, 400

            ayatct = FindAyatCountIn(surahnumber)
            for an in range(1, ayatct + 1):
                hifz = HifzModel.FindHifzBySurahAndNumber(str(current_identity.id), surahnumber, an)
                if not hifz: return {"message": "Some ayat in surah does not exist"}, 400
                try:
                    hifz.delete_from_db()
                except:
                    return {"message": "An error occurred deleting the data."}, 500
            return {}, 200

        if juz and not surahnumber and not ayatnumber:
            if not JuzInRange(juz):
                return {"message": "Juz is not valid"}, 400

            # a list of tuples where each tuple will contain a surah number and its last ayat that is contained within that juz
            limits_dict = FindSurahWithAyatInJuz(juz)
            for (sn,limits) in limits_dict.items():
                for an in range(limits[0], limits[1] + 1):
                    hifz = HifzModel.FindHifzBySurahAndNumber(str(current_identity.id), sn, an)
                    if not hifz: return {"message": "Some ayat in juz does not exist"}, 400
                    try:
                        hifz.delete_from_db()
                    except:
                        return {"message": "An error occurred deleting the data."}, 500
            return {}, 200
        return {'Some parameters are missing!'}, 400



    @jwt_required()
    def put(self):
        data = Hifz.parser.parse_args()
        surahnumber = data.get('surah')
        ayatnumber = data.get('ayatnumber')
        if ayatnumber:
            ayatnumber = ayatnumber.replace("\'","\"") # to satisfy json loads requirement, need to replace single quotes with double quotesu

            ayatnumber = json.loads(ayatnumber)

        juz = data.get('juz')

        if surahnumber and ayatnumber:

            if not isSurahValid(surahnumber):
                return {'message': "Surah is not valid"}, 400

            if  isinstance(ayatnumber, dict):
                # sanity checking
                if not ayatnumber.get('start') or not ayatnumber.get('end'):
                    return {'message': "Invalid ayat limits format"}, 400
                else:
                    if not AyatIsInRange(surahnumber, ayatnumber.get('start')) or not AyatIsInRange(surahnumber, ayatnumber.get('end')):
                        return {'message': "Either limit is out of range"}, 400
                
                # start saving
                saved_array = []
                for an in range(ayatnumber.get('start'), ayatnumber.get('end') + 1):
                    hifz = HifzModel.FindHifzBySurahAndNumber(str(current_identity.id), surahnumber, an)
                    if not hifz: hifz = HifzModel(str(current_identity.id), surahnumber, an)
                    hifz = modify_properties(hifz, data)
                    try:
                        hifz.save_to_db()
                        saved_array.append(hifz.json());
                    except:
                        return {"message": "An error occurred updating the data."}, 500
                return {'ayats': saved_array};
            else:
                if not AyatIsInRange(surahnumber, ayatnumber):
                    return {'message': "Ayat is out of range"}, 400

                hifz = HifzModel.FindHifzBySurahAndNumber(str(current_identity.id), surahnumber, ayatnumber)
                if not hifz: hifz = HifzModel(str(current_identity.id), surahnumber, ayatnumber)
                hifz = modify_properties(hifz, data)

                try:
                    hifz.save_to_db()
                except:
                    return {"message": "An error occurred updating the data."}, 500

                return hifz.json(), 200


        if surahnumber and not ayatnumber:
            if not isSurahValid(surahnumber):
                return {'message': "Surah is not valid"}, 400

            ayatct = FindAyatCountIn(surahnumber)
            saved_array = []
            for an in range(1, ayatct + 1):
                hifz = HifzModel.FindHifzBySurahAndNumber(str(current_identity.id), surahnumber, an)
                if not hifz: hifz = HifzModel(str(current_identity.id), surahnumber, an)
                hifz = modify_properties(hifz, data)
                try:
                    hifz.save_to_db()
                    saved_array.append(hifz.json())
                except:
                    return {"message": "An error occurred updating the data."}, 500
            return {'surah': surahnumber, 'ayats': saved_array}, 200

        if juz and not surahnumber and not ayatnumber:
            if not JuzInRange(juz):
                return {"message": "Juz is not valid"}, 400

            # a list of tuples where each tuple will contain a surah number and its last ayat that is contained within that juz
            limits_dict = FindSurahWithAyatInJuz(juz)
            saved_array = []
            for (sn,limits) in limits_dict.items():
                for an in range(limits[0], limits[1] + 1):
                    hifz = HifzModel.FindHifzBySurahAndNumber(str(current_identity.id), sn, an)
                    if not hifz: hifz = HifzModel(str(current_identity.id), sn, an)
                    hifz = modify_properties(hifz, data)
                    try:
                        hifz.save_to_db()
                        saved_array.append(hifz.json())
                    except:
                        return {"message": "An error occurred inserting the data."}, 500
            return {'juz': juz, 'ayats': saved_array}, 200
        return {'Some parameters are missing!'}, 400


# class MemorizedAyats(Resource):
    @jwt_required()
    def get(self):
        data = Hifz.parser.parse_args()
        surah = data.get('surah')
        juz = data.get('juz')
        ayat = data.get('ayatnumber')
        start = data.get('start')
        end = data.get('end')



        if surah and start and end and not ayat:
            return {'ayats': list(map(lambda x: x.json(), HifzModel.FindByRange(str(current_identity.id), surah, start, end)
                ))  }, 200

        if surah and ayat:
            # print("returning filtered by ayat")
            return {'ayats': list(map(lambda x: x.json(), HifzModel.query.filter_by(ownerID=str(current_identity.id), surah=surah, ayatnumber=ayat)))  }, 200

        if surah and not ayat:
          # print("returning filtered by surah")
            return {'ayats': list(map(lambda x: x.json(), HifzModel.query.filter_by(ownerID=str(current_identity.id), surah=surah )))  }, 200

        if juz:
          # print("returning filtered by juz")
            return {'ayats': list(map(lambda x: x.json(), HifzModel.query.filter_by(ownerID=str(current_identity.id), juz=juz )))  }, 200


        return {'ayats': list(map(lambda x: x.json(), HifzModel.query.filter_by(ownerID=str(current_identity.id)  )))  }, 200




def modify_properties(hifz, data):
    import pdb
    if data.get('theme'):
        hifz.theme = data.get('theme')
    if data.get('date_refreshed'):
        hifz.last_refreshed = data.get('date_refreshed')
    if data.get('group'):
        hifz.group = data.get('group')
    if data.get('difficulty'):
        hifz.difficulty = data.get('difficulty')
    if data.get('note'):
        hifz.note = data.get('note')
    if data.get('just_revisited'):
        hifz.revisit_frequency += 1

    return hifz


class HifzRecommendation(Resource):
    parser.add_argument('surah',
        type=int,
        required=False,
        help="Filter by surah number that you memorized"
    )

    parser.add_argument('random',
        type=bool,
        required=False,
        help="Specify whether the recommendation will be based on a random selection"
    )

    parser.add_argument('all_users'
        type=bool,
        required=False,
        help="Dictates whether data will be analyzed by user's own hifz or by the all user's hifz"
    )

     parser.add_argument('start',
        type=int,
        required=False,
        help="starting range of ayat from which to filter from"
    )

    parser.add_argument('end',
        type=int,
        required=False,
        help="the ending range of ayat at which to end filtering from"
    )

    parser.add_argument('theme',
        type=str,
        required=False,
        help="Filter by the theme of the ayat"
    )

    parser.add_argument('juz',
        type=int,
        required=False,
        help="filter by the juz number that was memorized"
    )

    parser.add_argument('difficulty',
        type=int,
        required=False,
        help="Filter by ayat's difficulty"
    )

    parser.add_argument('group',
        type=str,
        required=False,
        help="Filter by group of similar ayats"
    )

    @jwt_required()
    def get(self):
        data = Hifz.parser.parse_args()
        surah = data.get('surah')
        juz = data.get('juz')
        start = data.get('start')
        random = data.get('random')

        difficulty = data.get('difficulty')
        theme = data.get('theme')
        group = data.get('group')

        if random:
            if surah and start and end and not ayat:
                if all_users:
                    ayats = list(map(lambda x: x.json(), HifzModel.FindByRange(None, surah, start, end)))
                else:    
                    ayats = list(map(lambda x: x.json(), HifzModel.FindByRange(str(current_identity.id), surah, start, end)
                ))
                idx = random.randint(0, len(ayats))
                return {'selected':   ayats[idx] }, 200

            if surah and not ayat:
                if all_users:
                    ayats = list(map(lambda x: x.json(), HifzModel.query.filter_by(surah=surah )))
                else:    
                    ayats = list(map(lambda x: x.json(), HifzModel.query.filter_by(ownerID=str(current_identity.id), surah=surah )))
                idx = random.randint(0, len(ayats))
                return {'selected':   ayats[idx] }, 200

            if juz:
                if all_users:
                    ayats = list(map(lambda x: x.json(), HifzModel.query.filter_by(juz=juz )))
                else:    
                    ayats = list(map(lambda x: x.json(), HifzModel.query.filter_by(ownerID=str(current_identity.id), juz=juz )))
                idx = random.randint(0, len(ayats))
                return {'selected':   ayats[idx] }, 200

            if all_users:
                ayats = list(map(lambda x: x.json(), HifzModel.query.all()))
            else:
                ayats = list(map(lambda x: x.json(), HifzModel.query.filter_by(ownerID=str(current_identity.id)  )))
            return {'selected':   ayats[idx] }, 200

        else:
            if all_users:
                ayats = list(map(lambda x: x.json(), HifzModel.query.all()))
            else:
                ayats = list(map(lambda x: x.json(), HifzModel.query.filter_by(ownerID=str(current_identity.id)  )))
            if [difficulty, theme, group].count(True) != 1:
                return {"message" : "ayat can only be filtered by either difficulty, theme or group"} 

            if not any(difficulty, theme, group): 
                return {"message" : "no filter criteria specified"}               

            if difficulty:
                filtered = [a if a.difficulty == difficulty for a in ayats]

            if group:
                filtered = [a if a.group == group for a in ayats]

            if theme:
                filtered = [a if a.theme == theme for a in ayats]

            

            return {'selected' : [a.json for a in filtered]}






        
