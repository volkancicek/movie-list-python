import inspect
import os
import sys

import pytest

current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from movie_app.app import create_app, db, Movies, People, Person_Movie
from movie_app.services.db_service import get_db


@pytest.fixture(scope='module')
def test_client():
    flask_app = create_app('app_test.cfg')
    testing_client = flask_app.test_client()
    ctx = flask_app.app_context()
    ctx.push()

    yield testing_client  # this is where the testing happens!

    ctx.pop()


@pytest.fixture(scope='module')
def init_database():
    db.create_all()

    movie = Movies(title='my neighbor totoro', ghibli_id='xxxxxxx')
    person = People(name='totoro', ghibli_id='xxxxxxx')
    db.session.add(movie)
    db.session.add(person)
    statement = Person_Movie.insert().values(film_id='xxxxxxx', person_id='xxxxxxx')
    db.session.execute(statement)
    db.session.commit()

    yield db

    db.drop_all()
