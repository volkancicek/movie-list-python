import requests

base_url = 'https://ghibliapi.herokuapp.com/{0}'


def get_all_people():
    p = requests.get(base_url.format('people'))
    people = p.json()

    return people


def get_all_films():
    f = requests.get(base_url.format('films'))
    films = f.json()

    return films
