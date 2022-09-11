from sqlalchemy import Column,Integer,String,asc
from sqlalchemy.orm import sessionmaker
from config.bd import Base,engine

Session = sessionmaker(bind=engine)
# pregunta
class Question(Base):
    __tablename__= 'question'
    id_question = Column(Integer,primary_key=True,autoincrement=True)
    text_question = Column(String(3000),nullable=False)
    prerequisites = Column(String(3000),nullable=True)
    posrequisites = Column(String(3000), nullable=True)
    valor = Column(String(100), nullable=True)
    console = Column(String(100), nullable=True)

    def getQuestion(number):
        session = Session()
        question = session.query(Question).filter(Question.id_question == number).first()
        session.close()
        return question

    def nextQuestion(idquestion):
        session = Session()
        question = session.query(Question)\
            .filter(Question.id_question > idquestion)\
            .order_by(asc(Question.id_question)).limit(1).first()
        session.close()
        return question