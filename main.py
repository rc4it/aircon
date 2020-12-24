from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.orm import sessionmaker
from scraper import scraper

# creating database
URI = 'mysql://root:Password1@localhost/aircon'
engine = create_engine(URI, echo = True)
Base = declarative_base()

# database structure
class User(Base):  
    __tablename__ = 'users'
    
    tele_handle = Column(String(20),primary_key=True)
    meterID = Column(String(10))
    room_num = Column(String(10))
    lower_limit = Column(Integer())

Base.metadata.create_all(engine)

# starting session
Session = sessionmaker(bind = engine)
session = Session()

# returns True if credentials are valid 
def validAcc(meterID,room_num):
    return scraper(meterID,room_num) != None


# FIRST STATE
def userInput():  
    # user inputs from telegram 
    tele_handle = input('tele handle ')  
    meterID = input('meterID (8 digits)')
    room_num = input('room num (#xx-xxx) or (#xx-xx)')
    lower_limit = input('lower limit (1 digit)')

    # checking if user input is valid 
    if not validAcc(meterID,room_num):
        print('wrong credentials')
        return 
    
    # checking if user has an existing account by searching for tele handle
    unique_user = session.query(User).get(tele_handle)  # will return None if cannot find 

    if unique_user:  # if user has existing account 
        unique_user.meterID = meterID
        unique_user.room_num = room_num
        unique_user.lower_limit = lower_limit

        session.commit()

    else:  # if user does not have existing account 
        user = User(tele_handle = tele_handle,meterID = meterID, room_num = room_num, lower_limit = lower_limit)

        session.add(user)
        session.commit()
    

def changeRoom():  
    # filter out specific user from database using tele handle
    tele_handle = input('tele handle ')
    user = session.query(User).get(tele_handle)

    # changing room details
    new_meterID = input('meterID (8 digits)')
    new_room_num = input('room_num (#xx-xxx) or (#xx-xx)')

    if not validAcc(new_meterID,new_room_num):
        print('wrong credentials')
        return

    user.meterID = new_meterID
    user.room_num = new_room_num

    session.commit()


def changeLowerLimit():
    # filter out user from database using tele handle
    tele_handle = input('tele handle ')
    user = session.query(User).get(tele_handle)

    # changing lower limit
    user.lower_limit = input('new lower limit (1 digit)')

    session.commit()


def checkBalance():
    # filter out user from database using tele handle
    tele_handle = input('tele handle ')
    
    user = session.query(User).get(tele_handle)

    # getting meterID & room_num 
    meterID = user.meterID
    room_num = user.room_num

    # pass in meterID & password to scraper 
    balance = scraper(meterID,room_num)

    print(balance)

