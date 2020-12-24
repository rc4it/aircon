import requests
from bs4 import BeautifulSoup

# user input
meterID = '10001103'  
room = '#13-01A'  

def scraper(meterID,room):

    # deriving password 
    floor = room[1:3]
    unit = room[4:]
    password = '06' + floor + '0' + unit 

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

print(scraper(meterID,room))




