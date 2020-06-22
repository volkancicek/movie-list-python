# movie-list-python-flask
A flask web app that retrieves movies and people in them from ghibli api [https://ghibliapi.herokuapp.com/] and lists.

## Build & Run

with commands:

`pip install -r src/requirements.txt`

`python src/movie_app/app.py`

with dockerfile:

`docker build -t movies:latest .`

`docker run movies:latest`


## url

plain list of all movies from the Ghibli API including the people that
appear in it.

[localhost:8000/movies/]

## To Dos

* extend unit tests to cover api, db, and schedule services and refresh movies feature
* add cache to prevent interruptions when updating db
