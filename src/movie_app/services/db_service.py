from flask_sqlalchemy import SQLAlchemy


def clear_data(db):
    """ a function to remove existing records from DB"""
    meta = db.metadata
    for table in reversed(meta.sorted_tables):
        db.session.execute(table.delete())
    db.session.commit()


def get_db(app):
    db = SQLAlchemy(app)
    return db
