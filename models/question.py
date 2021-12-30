from sqlalchemy import Column,Integer,String
from sqlalchemy.orm import sessionmaker
from config.bd import Base,engine
# pregunta
class Question(Base):
    __tablename__= 'question'
    id_question = Column(Integer,primary_key=True,autoincrement=True)
    text_question = Column(String(3000),nullable=False)
    # solucion?

def getQuestion(number):
    Session = sessionmaker(bind=engine)
    session = Session()
    question = session.query(Question).filter(Question.id_question == number).first()
    session.close()
    return question