import atexit
import os
import sys
from datetime import datetime

from flask import Flask, render_template, Blueprint

import services.api_service as api
import services.db_service as db_service
from services.schedule_service import Scheduler

sys.path.append(os.path.dirname(__file__))

movies_bp = Blueprint('movies_bp', __name__, template_folder='templates', static_folder='static')


def create_app(conf):
    """ a function to create app using config file """
    new_app = Flask(__name__, instance_relative_config=False)
    new_app.config.from_pyfile(conf)
    new_app.register_blueprint(movies_bp)
    return new_app


app = create_app('app.cfg')
db = db_service.get_db(app)
scheduler = Scheduler()
"""drop db at exit"""
atexit.register(lambda: db.drop_all())

""" relation table"""
Person_Movie = db.Table('person_movie', db.Column('person_id', db.String(36), db.ForeignKey('people.ghibli_id')),
                        db.Column('film_id', db.String(36), db.ForeignKey('movies.ghibli_id')))

"""SQLAlchemy objects"""


class Movies(db.Model):
    __tablename__ = 'movies'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(20))
    ghibli_id = db.Column(db.String(36))
    people = db.relationship("People", secondary=Person_Movie, cascade="delete")


class People(db.Model):
    __tablename__ = 'people'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20))
    ghibli_id = db.Column(db.String(36))


def refresh_movies():
    """ a function that clears db, gets from ghibli api again and then saves to db"""
    db_service.clear_data(db)
    films = api.get_all_films()
    people = api.get_all_people()
    save_movies_to_db(films, people)


def save_movies_to_db(films, people):
    """ a function that saves movies and related people to DB"""
    for i in range(len(films)):
        db.session.add(Movies(title=films[i]['title'], ghibli_id=films[i]['id']))
        db.session.commit()
    for i in range(len(people)):
        person_id = people[i]['id']
        db.session.add(People(name=people[i]['name'], ghibli_id=person_id))
        db.session.commit()
        films = people[i]['films']
        for j in range(len(films)):
            film_id = films[j].split("/")[-1]
            statement = Person_Movie.insert().values(film_id=film_id, person_id=person_id)
            db.session.execute(statement)
            db.session.commit()
    scheduler.movies_update_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def main():
    """ main function"""
    db.create_all()
    refresh_movies()
    scheduler.schedule_background_job(refresh_movies, 50)
    port = int(os.environ.get('PORT', 8000))
    app.run(host='localhost', port=port)


@movies_bp.route('/')
@app.route('/')
def index():
    ret_str = "{0}, App is running...   Movies were updated at {1}".format(
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        scheduler.movies_update_time)
    return ret_str


@movies_bp.route('/movies/', methods=['GET'])
@app.route('/movies/', methods=['GET'])
def movies():
    all_movies = Movies.query.all()

    return render_template('movies.html', movies=all_movies, update=scheduler.movies_update_time,
                           curr=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))


if __name__ == '__main__':
    main()
