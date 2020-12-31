import requests
from bs4 import BeautifulSoup

def scraper(meterID,room):

    # deriving password 
    floor = room[1:3]
    unit = room[4:]
    password = '06' + floor + '0' + unit  # for suite 

    if len(password) != 8:  # for non suite
        password += 'N'

    payload = {
        'txtLoginId': meterID, 
        'txtPassword': password,
        'btnLogin' : 'Login'
        }

    s = requests.session()

    r = s.post('https://nus-utown.evs.com.sg/EVSEntApp-war/loginServlet',data=payload)
    r = s.get('https://nus-utown.evs.com.sg/EVSEntApp-war/viewMeterCreditServlet')

    soup = BeautifulSoup(r.text,'html.parser')

    try: 
        txt = soup.find_all(class_ = 'mainContent_normalText')[1]
        return txt.get_text()
    except:
        return None

balance = scraper('10001103','#13-01A')
index = balance.index('$')
value = float(balance[index+2:])

def lowerLimitCheck(value):
    if value < lower_credit_limit:
        text = 'You have $' + value + ' remaining. \nYou can top up at https://nus-utown.evs.com.sg/.' 











