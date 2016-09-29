from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()


class User(Base):
    __tablename__ = 'user'

    name = Column(String(250), nullable=False)
    id = Column(Integer, primary_key=True)
    email = Column(String(250), nullable=False)
    picture = Column(String(250))


class Serializeable():
    @classmethod
    def serialize_list(cls, inputList):
        return [i.serialize for i in inputList]


class Category(Base, Serializeable):
    __tablename__ = 'category'

    name = Column(String(250), nullable=False)
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
        """Return object data in an easily serializable format."""
        return {
            'name': self.name,
            'id': self.id
        }


class Item(Base, Serializeable):
    __tablename__ = 'item'

    name = Column(String(250), nullable=False)
    id = Column(Integer, primary_key=True)
    description = Column(String(250))
    category_id = Column(Integer, ForeignKey('category.id'))
    category = relationship(Category)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
        return {
            'name': self.name,
            'id': self.id,
            'description': self.description,
            'category_id': self.category_id,
            'category_name': self.category.name
        }

engine = create_engine('sqlite:///itemcatalog.db')


Base.metadata.create_all(engine)
