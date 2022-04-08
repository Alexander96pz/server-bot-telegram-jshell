from sqlalchemy import Column,Integer,String,Boolean,DateTime
import datetime
from sqlalchemy.orm import relationship
from sqlalchemy.orm import sessionmaker
from config.bd import Base,engine

class User(Base):
    __tablename__ = 'user'
    id_user = Column(Integer,primary_key=True,unique=True)
    first_name = Column(String(50),nullable=False)
    is_bot = Column(Boolean, nullable=True)
    username = Column(String(50),nullable=False)
    lenguaje_code = Column(String(50),nullable=True)
    createdAt = Column(DateTime,default=datetime.datetime.now())
    id_message = relationship("Message")

    def addUser(update):
        Session = sessionmaker(bind=engine)
        session = Session()
        user = User(id_user=update._effective_user.id,
            first_name=update._effective_user.first_name,
            is_bot=update._effective_user.is_bot,
            username=update._effective_user.username,
            lenguaje_code=update._effective_user.language_code)
        session.add(user)
        session.commit()
        session.close()

    def findUser(id_user):
        Session = sessionmaker(bind=engine)
        session = Session()
        user = session.query(User).filter(User.id_user == id_user).first()
        session.close()
        return user