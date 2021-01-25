from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, create_engine, Float
from sqlalchemy.orm import sessionmaker

sqlID = 'root'
sqlPASSWORD = 'Password1'
URI = 'mysql://' + sqlID + ':' + sqlPASSWORD + '@localhost/aircon'

engine = create_engine(URI, echo = True)
Base = declarative_base()

# table structure
class User(Base):  
    __tablename__ = 'users'
    
    username = Column(String(100),primary_key=True)
    evs_username = Column(String(10))
    room_unit_no = Column(String(10))
    lower_credit_limit = Column(Float(100))

Base.metadata.create_all(engine)

# starting session
Session = sessionmaker(bind = engine)


#user = session.query(User).get(username)
#user.evs_username = user_input
#session.commit()