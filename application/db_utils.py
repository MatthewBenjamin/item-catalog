# db_utils.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dbsetup import Base, User, Item

# Connect to Database and create database session
engine = create_engine('sqlite:///itemcatalog.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


def get_by_id(model, lookup_id):
    result = session.query(model).filter_by(id=lookup_id).one()
    return result


def get_user_id(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


def save_record(newRecord):
    session.add(newRecord)
    session.commit()


def create_user(login_session):
    new_user = User(name=login_session['name'],
                    email=login_session['email'],
                    picture=login_session['picture'])
    save_record(new_user)
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def delete_category_items(category_id):
    session.query(Item).filter_by(
        category_id=category_id).delete()


def delete_record(record_to_delete):
    session.delete(record_to_delete)
    session.commit()
