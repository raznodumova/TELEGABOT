import sqlalchemy as sq
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class User(Base):
    __tablename__ = 'user'
    id = sq.Column(sq.Integer, primary_key=True)
    cid = sq.Column(sq.BigInteger, unique=True)


class Word(Base):
    __tablename__ = 'word'
    id = sq.Column(sq.Integer, primary_key=True)
    word = sq.Column(sq.String(length=40), unique=True)
    translate = sq.Column(sq.String(length=40), unique=True)


class UserWord(Base):
    __tablename__ = 'user_word'
    id = sq.Column(sq.Integer, primary_key=True)
    word = sq.Column(sq.String(length=40), unique=True)
    translate = sq.Column(sq.String(length=40), unique=True)
    id_user = sq.Column(sq.Integer, sq.ForeignKey('user.id'), nullable=False)

    user = relationship(User, backref='word')


def create_tables(engine):
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)