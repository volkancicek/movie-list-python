import os
from datetime import datetime
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from services.api_service import get_all_films, get_all_people
from services.scheduler import Scheduler


def create_app(conf):
    """ a function to create app using config file """
    app = Flask(__name__, instance_relative_config=False)
    app.config.from_pyfile(conf)
    return app


app = create_app('app.cfg')
db = SQLAlchemy(app)
scheduler = Scheduler()

""" SQLAlchemy classes and relation table"""
Person_Movie = db.Table('person_movie', db.Column('person_id', db.String(36), db.ForeignKey('people.ghibli_id')),
                        db.Column('film_id', db.String(36), db.ForeignKey('movies.ghibli_id')))


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


""" SQLAlchemy """


def refresh_movies():
    """ a function to clear movies at DB and then get from ghibli api again"""
    clear_data()
    save_movies_to_db()


def clear_data():
    """ a function to remove existing records from DB"""
    meta = db.metadata
    for table in reversed(meta.sorted_tables):
        db.session.execute(table.delete())
    db.session.commit()


def save_movies_to_db():
    """ a function that retrieves movies and related people from ghibli api and saves to DB"""
    films = get_all_films()
    for i in range(len(films)):
        db.session.add(Movies(title=films[i]['title'], ghibli_id=films[i]['id']))
        db.session.commit()
    people = get_all_people()
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


@app.route('/')
def index():
    ret_str = "{0}, App is running...   Movies were updated at {1}".format(
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        scheduler.movies_update_time)
    return ret_str


@app.route('/movies/', methods=['GET'])
def movies():
    all_movies = Movies.query.all()

    return render_template('movies.html', movies=all_movies, update=scheduler.movies_update_time,
                           curr=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))


if __name__ == '__main__':
    main()
