from config.bd import Base,engine
from sqlalchemy import Column,Integer,String,Boolean
from sqlalchemy.orm import sessionmaker

Session = sessionmaker(bind=engine)
class Answer(Base):
    __tablename__ = 'answer'
    id_answer = Column(Integer, primary_key=True, unique=True, autoincrement=True)
    text_answer = Column(String(400), nullable=True)
    analysis_dynamic = Column(Boolean, nullable=False)
    analysis_static = Column(Boolean, nullable=False,default=True)

    def add_Answer(text_answer, analysis_dynamic, analysis_static):
        session = Session()
        answer = Answer(text_answer=text_answer,
                        analysis_dynamic=analysis_dynamic,
                        analysis_static=analysis_static)
        session.add(answer)
        session.commit()
        session.refresh(answer)
        session.close()
        return answer
        