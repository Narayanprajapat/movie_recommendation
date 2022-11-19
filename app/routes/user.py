from flask import Blueprint, request
from app.helper.responseMaker import response_maker
import datetime
import json
import math

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
        find_user_data = [user for user in user_data_json if int(user['user_id']) == int(user_id)]
        current_day = datetime.date.today()
        current_date_format = dateFormat(datetime.date.strftime(current_day, "%m/%d/%Y"))

        # user not exist random output
        if len(find_user_data) == 0:
            movie_resp = random_recommendation(movie_json, current_date_format)
            return response_maker({'message': 'User not exist', "data": top_ten_sorted(movie_resp)}, 200)

        # user preference if not exist user in user preference
        user_preference_data = find_user(user_id, user_preference_json)
        if len(user_preference_data) == 0:
            movie_resp = random_recommendation(movie_json, current_date_format)
            return response_maker({'message': 'No user preference', "data": top_ten_sorted(movie_resp)}, 200)

        # related user
        user_preference_data = user_preference_data[0]
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
                        genres[genre] = genres[genre] + preference_score
                    else:
                        genres[genre] = preference_score
            except Exception as e:
                pass

        for genre in genres:
            genres[genre] = math.ceil(genres[genre] / len(related_user_data))

        for up in user_preference_data['preference']:
            if up['genre'] in genres:
                genres[up['genre']] = genres[up['genre']] + up['preference_score']
            else:
                genres[up['genre']] = up['preference_score']

        # Current date

        find_movies_by_genre = dict()
        for genre in genres:
            find_movies_by_genre[genre] = movie_find_by_genre(genre, movie_json, current_date_format)

        count = sum([genres[i] for i in genres]) / 10  # 10 movies

        for gen in genres:
            genres[gen] = math.ceil(genres[gen] / count)

        sorted_genre = dict(sorted(genres.items(), key=lambda x: x[1], reverse=True))

        movies = get_movie_from_genre(sorted_genre, find_movies_by_genre)
        return response_maker({'message': 'success', 'data': top_ten_sorted(movies)}, 201)
    except Exception as e:
        print(e)
        return response_maker({'message': 'Internal server error'}, 500)


def find_user(user_id, json_data):
    user_data = [user for user in json_data if int(user['user_id']) == int(user_id)]
    return user_data


# Count days
def numOfDays(date1, date2):
    return (date2 - date1).days


# Date formate
def dateFormat(normalDate):
    splitDate = normalDate.split('/')
    return datetime.date(int(splitDate[2]), int(splitDate[0]), int(splitDate[1]))


def movie_find_by_genre(genre, movie_json, current_date_format):
    filter_movie_list = list()
    for i in movie_json:
        release_date = dateFormat(i['release_date'])
        i['old_days_count'] = numOfDays(release_date, current_date_format)
        if genre in i['genres']:
            filter_movie_list.append(i)

    sorted_movies = sorted(movie_json, key=lambda m: m['old_days_count'])
    return sorted_movies


def get_movie_from_genre(genra_order, genre_movie):
    print(genra_order, genre_movie)
    movie_list = list()

    for g in genra_order:
        count = genra_order[g]
        for gm in genre_movie[g]:
            if count != 0 or len(movie_list) != 0:
                if not gm['movie_id'] in movie_list:
                    if len(movie_list) == 10:
                        return movie_list
                    # del gm['old_days_count']
                    movie_list.append(gm)
            count = count - 1


def random_recommendation(movie_json, current_date_format):
    for i in movie_json:
        release_date = dateFormat(i['release_date'])
        i['old_days_count'] = numOfDays(release_date, current_date_format)

    sorted_movies = sorted(movie_json, key=lambda m: m['old_days_count'])

    movie_list = list()
    for m in sorted_movies:
        if len(movie_list) == 10:
            return movie_list
        # del m['old_days_count']
        movie_list.append(m)

    return movie_list


def top_ten_sorted(movies):
    sorted_movies = sorted(movies, key=lambda m: m['old_days_count'])
    movie_list = list()
    for m in sorted_movies:
        del m['old_days_count']
        movie_list.append(m)

    return movie_list
