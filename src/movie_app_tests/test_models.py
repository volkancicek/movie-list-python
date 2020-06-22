from movie_app.app import Movies


def test_get_movies_from_db(init_database):
    m = Movies.query.all()

    assert len(m) == 1
    assert len(m[0].people) == 1
    assert m[0].people[0].name == 'totoro'
