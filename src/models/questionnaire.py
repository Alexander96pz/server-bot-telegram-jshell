from sqlalchemy import Column,ForeignKey, Integer, DateTime
import datetime
from sqlalchemy.orm import sessionmaker
from config.bd import Base,engine
from models.message import Message
from models.answer import Answer
from sqlalchemy import desc

Session = sessionmaker(bind=engine)

class Questionnaire(Base):
    __tablename__ = 'questionnaire'
    id_questionnaire = Column(Integer,primary_key=True,unique=True,autoincrement=True)
    id_question = Column(ForeignKey("question.id_question"))
    id_message = Column(ForeignKey("message.id_message"))
    id_user = Column(ForeignKey("user.id_user"))
    id_answer = Column(ForeignKey("answer.id_answer"))
    # nos permitira conocer si la respuesta es correcta o no
    # isError= Column(Boolean,nullable=False)
    # text_answer=Column(String(400),nullable=True)
    # intento
    tried=Column(Integer,nullable=True,default=0)
    createdAt=Column(DateTime,default=datetime.datetime.now())

    # me extrae la ultima respuesta respondida correctamente
    def find_Questionnaire(id_user):
        session = Session()
        questionnaire = session.query(Questionnaire).join(Message)\
            .filter(Questionnaire.id_message == Message.id_message)\
            .filter(Questionnaire.id_user == id_user)\
            .filter(Questionnaire.id_answer == Answer.id_answer)\
            .filter(Answer.analysis_dynamic == False)\
            .filter(Answer.analysis_static == False)\
            .order_by(desc(Questionnaire.id_questionnaire)).first()
        session.close()
        # questionnaire=("questionario: ",questionnaire.id_questionnaire)
        return questionnaire

    def addQuestionnaire(id_question, id_message, id_user, id_answer, nroTried=0):
        session = Session()
        questionnaire = Questionnaire(id_question=id_question,
                                      id_message=id_message,
                                      id_user=id_user,
                                      id_answer=id_answer,
                                      # isError=isError,
                                      # text_answer=text_answer,
                                      tried=nroTried)
        session.add(questionnaire)
        # session.refresh(questionnaire)
        session.commit()
        session.close()
        return questionnaire

