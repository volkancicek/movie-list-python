import requests


def get_all_people():
    p = requests.get('https://ghibliapi.herokuapp.com/people')
    people = p.json()

    return people


def get_all_films():
    f = requests.get('https://ghibliapi.herokuapp.com/films')
    films = f.json()

    return films
