from flask import Flask, render_template
import os
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from api_service import get_all_films, get_all_people
from scheduler import Scheduler

basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'app.sqlite')
app = Flask(__name__)
db = SQLAlchemy(app)
scheduler = Scheduler()

Person_Movie = db.Table('person_movie',
                        db.Column('person_id', db.String(36), db.ForeignKey('people.ghibli_id')),
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


def refresh_movies():
    clear_db()
    save_movies_to_db()


def clear_db():
    delete_m = Movies.__table__.delete()
    db.session.execute(delete_m)
    delete_p = People.__table__.delete()
    db.session.execute(delete_p)
    db.session.commit()


def save_movies_to_db():
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
    db.create_all()
    save_movies_to_db()
    scheduler.schedule_background_job(refresh_movies, 60)
    port = int(os.environ.get('PORT', 8000))
    app.run(host='localhost', port=port)


@app.route('/')
def default():
    return "{0}, App is running.. \n Movies were updated at {1}".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                                                        scheduler.movies_update_time)


@app.route('/movies/', methods=['GET'])
def movies():
    all_movies = Movies.query.all()

    return render_template('movies.html', movies=all_movies, update=scheduler.movies_update_time)


if __name__ == '__main__':
    main()
