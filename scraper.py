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
        balance = txt.get_text()
        index = balance.index('$')
        return float(balance[index+2:])
    except:
        return None















