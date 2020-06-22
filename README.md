# movie-list-python-flask
A flask web app that retrieves movies and people in them from ghibli api [https://ghibliapi.herokuapp.com/] and lists.

## Build & Run

with commands:

`pip install -r src/requirements.txt`

`python src/movie_app/app.py`

with dockerfile:

`docker build -t movies:latest .`

`docker run movies:latest`


## urls 
index

[http://localhost:8000/]


plain list of all movies from the Ghibli API including the people that
appear in it.

[http://localhost:8000/movies/]
