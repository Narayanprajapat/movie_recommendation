import pdb

from flask import Blueprint, request
from app.helper.responseMaker import response_maker
from datetime import datetime
import json

user_blueprint = Blueprint('user_blueprint', __name__, template_folder="template")


@user_blueprint.route("/users", methods=["GET"])
def fetch_movie():
    path = 'static/files/'
    user_data_file_name = "user_data.json"
    user_preference_file_name = "user_preference.json"
    related_users_file_name = "related_users.json"
    movie_file_name = "movie_data.json"

    try:
        user_id = request.args['user_id']
    except Exception as e:
        print(e)
        return response_maker({'message': 'Please check user data'}, 500)

    try:
        user_data_json = json.load(open(path + user_data_file_name))
    except Exception as e:
        print(e)
        return response_maker({'message': 'Please check user data'}, 500)

    try:
        user_preference_json = json.load(open(path + user_preference_file_name))
    except Exception as e:
        print(e)
        return response_maker({'message': 'Please check user preference data'}, 500)

    try:
        related_users_json = json.load(open(path + related_users_file_name))
    except Exception as e:
        print(e)
        return response_maker({'message': 'Please check related users data'}, 500)

    try:
        movie_json = json.load(open(path + movie_file_name))
    except Exception as e:
        print(e)
        return response_maker({'message': 'Please check movie data'}, 500)

    try:
        print(user_id)
        find_user_data = [user for user in user_data_json if int(user['user_id']) == int(user_id)]
        # pdb.set_trace()
        if len(find_user_data) == 0:
            return response_maker({'message': 'User not exist'}, 400)

        find_user_data = find_user_data[0]
        user_preference_data = find_user(user_id, user_preference_json)[0]
        related_user_data = related_users_json[str(user_id)]
        genres = dict()
        for related_user in related_user_data:
            user_preference_resp = find_user(related_user['user_id'], user_preference_json)
            try:
                user_preference_resp = user_preference_resp[0]
                for preference in user_preference_resp['preference']:
                    genre = preference['genre']
                    preference_score = preference['preference_score']
                    if genre in genres:
                        genres[genre] = genres[genre] + 1
                        # genres[genre] = genres[genre] + preference_score
                    else:
                        # genres[genre] = preference_score
                        genres[genre] = 1
            except Exception as e:
                pass

        print(genres)
        print(len(related_user_data))
        print(user_preference_data)
        return response_maker({'message': 'success'}, 201)
    except Exception as e:
        print(e)
        return response_maker({'message': 'Internal server error'}, 500)


def find_user(user_id, json_data):
    user_data = [user for user in json_data if int(user['user_id']) == int(user_id)]
    return user_data
