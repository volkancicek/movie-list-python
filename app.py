import atexit
from flask import Flask, render_template
import os
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_migrate import Migrate
from api_service import get_all_films, get_all_people

basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'app.sqlite')
app.config['SQLALCHEMY_MIGRATE_REPO'] = os.path.join(basedir, 'db_repository')
app = Flask(__name__)

db = SQLAlchemy(app)

ma = Marshmallow(app)
migrate = Migrate(app, db)

person_movie_relation = db.Table('person_movie_relation',
                                 db.Column('person_id', db.String(36), db.ForeignKey('people.ghibli_id')),
                                 db.Column('film_id', db.String(36), db.ForeignKey('movies.ghibli_id')))


class Movies(db.Model):
    __tablename__ = 'movies'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20))
    ghibli_id = db.Column(db.String(36))
    people = db.relationship("People", secondary=person_movie_relation)


class People(db.Model):
    __tablename__ = 'people'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20))
    ghibli_id = db.Column(db.String(36))


def save_movies_to_db():
    films = get_all_films()
    for i in range(len(films)):
        db.session.add(Movies(name=films[i]['title'], ghibli_id=films[i]['id']))
        db.session.commit()

    people = get_all_people()
    for i in range(len(people)):
        person_id = people[i]['id']
        db.session.add(People(name=people[i]['name'], ghibli_id=person_id))
        db.session.commit()
        films = people[i]['films']

        for j in range(len(films)):
            film_id = films[j].split("/")[-1]
            statement = person_movie_relation.insert().values(film_id=film_id, person_id=person_id)
            db.session.execute(statement)
            db.session.commit()


def main():
    db.create_all()
    save_movies_to_db()
    # schedule_background_job()
    port = int(os.environ.get('PORT', 8000))
    app.run(host='localhost', port=port)


def schedule_background_job():
    scheduler = BackgroundScheduler()
    scheduler.add_job(func=save_movies_to_db(), trigger="interval", seconds=600)
    scheduler.start()
    # Shut down the scheduler when exiting the app
    atexit.register(lambda: scheduler.shutdown())


@app.route('/')
def default():
    return "App is running..  {0}".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))


@app.route('/movies/', methods=['GET'])
def movies():
    all_movies = Movies.query.all()

    return render_template('movies.html', movies=all_movies)


if __name__ == '__main__':
    main()
