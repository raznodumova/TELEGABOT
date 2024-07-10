import sqlalchemy
from sqlalchemy.orm import sessionmaker
from DATABASE.db_models import Word, create_tables


class Connection():
    def __init__(self):
        self.engine = sqlalchemy.create_engine('postgresql://postgres:5728821q@localhost:5432/TELEGA')
        self.Session = sessionmaker(bind=self.engine)
        self.session = self.Session()

    def create_db(self):
        words = {
            'привет': 'hello',
            'кот': 'cat',
            'собака': 'dog',
            'мышь': 'mouse',
            'компьютер': 'computer',
            'стол': 'table',
            'стул': 'chair',
            'кровать': 'bed',
            'телевизор': 'television',
            'ноутбук': 'laptop',

        }
        create_tables(engine=self.engine)

        for i in words.items():
            self.session.add(Word(word=i[0], translate=i[1]))
            self.session.commit()

    def session_close(self):
        self.session.close()


if __name__ == '__main__':
    db = Connection()
    db.create_db()
    db.session_close()