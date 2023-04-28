import requests
from seleniumwire import webdriver
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support import expected_conditions as EC
import warnings 
warnings.filterwarnings(action='ignore', category=DeprecationWarning)
from time import sleep
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from seleniumwire.utils import decode
from datetime import datetime
import json
import os.path

def find_between( s, first, last ):
    try:
        start = s.index( first ) + len( first )
        end = s.index( last, start )
        return ( s[start:end] )
    except ValueError:
        return ( "" )

session = requests.Session()
clientsecret = ""
refreshtoken = ""
clientid = ""
access_token = ""
global giocatori

def StartUp():
    if not os.path.exists('Session.json') or os.stat('Session.json').st_size == 0:
        with open("Session.json", 'w') as outfile:
            outfile.write(json.dumps("{}", indent = 4))

# OSM API
def login(userName : str, password : str):
    options = webdriver.ChromeOptions()
    options.add_argument('--log-level=3')
    options.headless = False
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
    found = False
    while not found:
            driver.get("https://www.onlinesoccermanager.com/Login")
            sleep(3)
            WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.XPATH, r'//*[@id="page-privacynotice"]/div/div/div[2]/div[3]/div[2]/div[1]/div[1]/button')))
            (driver.find_element(By.XPATH, r'//*[@id="page-privacynotice"]/div/div/div[2]/div[3]/div[2]/div[1]/div[1]/button')).click()
            WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.XPATH, r'//*[@id="page-signup"]/div[3]/div[4]/div[2]/button')))
            (driver.find_element(By.XPATH, r'//*[@id="page-signup"]/div[3]/div[4]/div[2]/button')).click()
            WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.XPATH, r'//*[@id="manager-name"]')))
            sleep(3)
            (driver.find_element(By.XPATH, r'//*[@id="manager-name"]')).send_keys(userName)
            (driver.find_element(By.XPATH, r'//*[@id="password"]')).send_keys(password)
            (driver.find_element(By.XPATH, r'//*[@id="page-login"]/div[2]/div[3]/div[1]/div[1]/form/div[4]')).click()
            (driver.find_element(By.XPATH, r'//*[@id="password"]')).send_keys(Keys.RETURN)
            sleep(5)
            
            for request in driver.requests:
                if "token" in request.url and request.method == "POST":
                    body = decode(request.response.body, request.response.headers.get('Content-Encoding', 'identity'))
                    data = eval(body)
                    global refreshtoken
                    refreshtoken = data["refresh_token"]
                    global access_token
                    access_token = data["access_token"]
                    print("Logged in")
                    datasession = {}
                    biscotti = []
                    for cookie in driver.get_cookies():
                        session.cookies.set(cookie['name'], cookie['value'])
                        biscotti.append(cookie)
                    datasession["cookies"] = biscotti
                    datasession["access_token"] = access_token
                    datasession["refresh_token"] = refreshtoken
                    with open("Session.json", 'w') as outfile:
                        outfile.write(json.dumps(datasession, indent = 4))
                    driver.quit()
                    found  = True
                    break

def getTeam():
    headers = {
        "Host": "web-api.onlinesoccermanager.com",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/112.0",
        "Accept": "application/json; charset=utf-8",
        "Accept-Language": "en-GB, en-GB",
        "Accept-Encoding": "gzip, deflate, br",
        "Authorization": "Bearer " + access_token,
        "Content-Type": "application/json; charset=utf-8",
        "PlatformId": "11",
        "AppVersion": "3.177.1",
        "Origin": "https://en.onlinesoccermanager.com",
        "Connection": "keep-alive",
        "Referer": "https://en.onlinesoccermanager.com/",
    }
    data = session.get("https://web-api.onlinesoccermanager.com/api/v1/leagues/25826809/team/18/transfers", headers=headers)
    giocatori = data.text
    return eval(giocatori.replace("true", "True").replace("false", "False").replace("null", "None"))


def TimeCheck():
    headers = {
        "Host": "web-api.onlinesoccermanager.com",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/112.0",
        "Accept": "application/json; charset=utf-8",
        "Accept-Language": "en-GB, en-GB",
        "Accept-Encoding": "gzip, deflate, br",
        "Authorization": "Bearer " + access_token,
        "Content-Type": "application/json; charset=utf-8",
        "PlatformId": "11",
        "AppVersion": "3.177.1",
        "Origin": "https://en.onlinesoccermanager.com",
        "Connection": "keep-alive",
        "Referer": "https://en.onlinesoccermanager.com/",
    }
    time = eval((session.get("https://web-api.onlinesoccermanager.com/api/v1/leagues/25826809/teams/18/timers", headers=headers).text).replace("false", "False").replace("true", "True").replace("null", "None"))
    for i in range(0, len(time)):
        time[i]["currentTimestamp"] = datetime.fromtimestamp(time[i]["currentTimestamp"])
        time[i]["finishedTimestamp"] = datetime.fromtimestamp(time[i]["finishedTimestamp"]) 
        if time[i]["finishedTimestamp"] < datetime.now():
            if  "coach" in time[i]["title"]:
                #data = session.put("https://web-api.onlinesoccermanager.com/api/v1/leagues/25826809/teams/18/trainingsessions/" + #trovare cosa mettere qui +"/claim", headers=headers)
                print()
            else: print(time[i]["title"] + " has finished")
        elif time[i]["finishedTimestamp"] > datetime.now():
            if  "coach" in time[i]["title"]:
                print(time[i]["title"] + " is busy until " + str(time[i]["finishedTimestamp"]))
            elif "Your next match" in time[i]["title"]:
                print(time[i]["title"] + " will be " + str(time[i]["finishedTimestamp"]))

def Train(Giocatore : str, obiettivo : int):
    headers = {
        "Host": "web-api.onlinesoccermanager.com",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/112.0",
        "Accept": "application/json; charset=utf-8",
        "Accept-Language": "en-GB, en-GB",
        "Accept-Encoding": "gzip, deflate, br",
        "Authorization": "Bearer " + access_token,
        "Content-Type": "application/x-www-form-urlencoded; charset=utf-8",
        "PlatformId": "11",
        "AppVersion": "3.177.1",
        "Origin": "https://en.onlinesoccermanager.com",
        "Connection": "keep-alive",
        "Referer": "https://en.onlinesoccermanager.com/",
    }
    playerId = ""
    position  = ""
    for giocatore in giocatori:
        if giocatore["player"]["name"] == Giocatore:
            playerId = str(giocatore["player"]["id"])
            position = str(giocatore["player"]["position"])
            break
    payload = "playerId=" + playerId + "&trainer=" + position + "&timerGameSettingId=20"
    data = session.post("https://web-api.onlinesoccermanager.com/api/v1/leagues/25826809/teams/18/trainingsessions", headers=headers, data=payload)
    if data.status_code == 200:
        print("Training started")
    else:
        print("Trainer is busy with another player")

StartUp()
dataSession = ""
with open("Session.json", "r") as f:
    dataSession = json.load(f)
if dataSession == "{}":
    login("Frigge", "Nipotino04?")
elif not "cookies" in dataSession.keys() or not "access_token" in dataSession.keys() or  not "refresh_token" in dataSession.keys():
    login("Frigge", "Nipotino04?")
else:
    print("Session found!")
    for cookie in dataSession["cookies"]:
        session.cookies.set(cookie['name'], cookie['value'])
    access_token = dataSession["access_token"]
    refreshtoken = dataSession["refresh_token"]
giocatori = getTeam()
TimeCheck()
Train("Donnarumma", 88)
print()

