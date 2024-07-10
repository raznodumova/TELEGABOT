import sqlalchemy
from sqlalchemy.orm import sessionmaker
from DATABASE.db_models import User, Word, UserWord


class USER():

    def __init__(self, id, cid):
        self.id = id
        self.cid = cid

    def user_list(self, engine):
        session = (sessionmaker(bind=engine))()
        users = session.query(User).all()
        users = [self.cid for user in users]
        session.close()
        return users

    def add_users(self, engine, user_id):
        session = (sessionmaker(bind=engine))()
        session.add(User(cid=user_id))
        session.commit()
        session.close()

    def get_words(self, engine, user_id):
        session = (sessionmaker(bind=engine))()
        words = session.query(UserWord.word, UserWord.translate) \
            .join(User, self.id == UserWord.id_user) \
            .filter(User.cid == user_id).all()
        all_words = session.query(Word.word, Word.translate).all()
        result = all_words + words
        session.close()
        return result

    def add_words(self, engine, cid, word, translate):
        session = (sessionmaker(bind=engine))()
        id_user = session.query(User.id).filter(self.cid == cid).first()[0]
        session.add(UserWord(word=word, translate=translate, id_user=id_user))
        session.commit()
        session.close()

    def delete_words(self, engine, cid, word):
        session = (sessionmaker(bind=engine))()
        id_user = session.query(User.id).filter(self.cid == cid).first()[0]
        session.query(UserWord).filter(UserWord.id_user == id_user, UserWord.word == word).delete()
        session.commit()
        session.close()