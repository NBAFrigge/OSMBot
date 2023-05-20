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
import gzip

session = requests.Session()
clientsecret = ""
refreshtoken = ""
clientid = ""
access_token = ""
global giocatori
global userId
global TeamId
global LeagueId
global User
global Pwd
empty = {}

def findBetween(s, first, last ):
    try:
        start = s.index( first ) + len( first )
        end = s.index( last, start )
        return s[start:end]
    except ValueError:
        return ""

def StartUp():
    if not os.path.exists('Session.json') or os.stat('Session.json').st_size == 0:
        with open("Session.json", 'w') as outfile:
            outfile.write(json.dumps(empty, indent = 4))
    if not os.path.exists('Lineup.json') or os.stat('Lineup.json').st_size == 0:
        with open("Lineup.json", 'w') as outfile:
            outfile.write(json.dumps(empty, indent = 4))
    if not os.path.exists('Credential.json') or os.stat('Credential.json').st_size == 0:
        with open("Credential.json", 'w') as outfile:
            credential = {"username": "", "password": ""}
            outfile.write(json.dumps(credential, indent = 4))
    cred = {}
    with open("Credential.json", 'r') as outfile:
        cred = (json.load(outfile))
        if cred["username"] == "":
            cred["username"] = input("Insert username: ")
        if cred["password"] == "":
            cred["password"] = input("Insert password: ")
        global User
        User = cred["username"]
        global Pwd
        Pwd = cred["password"]
    with open("Credential.json", 'w') as outfile:
        outfile.write(json.dumps(cred, indent = 4))
    
        
  
# OSM API
def login(userName : str, password : str):
    options = webdriver.ChromeOptions()
    options.add_argument('--log-level=3')
    options.headless = False
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
    found1 = False
    found2 = False
    while not found2 and not found1:
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
                if not found1: 
                    if "https://web-api.onlinesoccermanager.com/api/token" == request.url and request.method == "POST":
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
                        with open("Session.json", 'r') as outfile:
                            datasession = json.load(outfile)
                        
                        datasession["cookies"] = biscotti
                        datasession["access_token"] = access_token
                        datasession["refresh_token"] = refreshtoken
                        with open("Session.json", 'w') as outfile:
                            outfile.write(json.dumps(datasession, indent = 4))
                        found1  = True
                if not found2:
                    if "batch" in request.url and request.method == "POST" and ("GET /v1/user/accounts HTTP/1.1").encode() in request.body:
                        body = gzip.decompress(request.response.body)
                        body = body.decode("utf-8")
                        userId = findBetween(body, '"masterAccountId":', ',"partnerNr":')
                        datasession = {}
                        with open("Session.json", 'r') as outfile:
                            datasession = json.load(outfile)
                        with open("Session.json", 'w') as outfile:
                            datasession["userId"] = userId
                            outfile.write(json.dumps(datasession, indent = 4))
                        found2 = True
                if found1 and found2:
                    driver.quit()
                    break

def getTeam():
    while 1:
        headers = {
            "Host": "web-api.onlinesoccermanager.com",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:109.0) Gecko/20100101 Firefox/112.0",
            "Accept": "application/json; charset=utf-8",
            "Accept-Language": "en-GB, en-GB",
            "Accept-Encoding": "gzip, deflate, br",
            "Authorization": "Bearer " + access_token,
            "Content-Type": "multipart/mixed; boundary=batch_5528b742-a7d1-409a-a607-c24e4918f2c2",
            "PlatformId": "11",
            "AppVersion": "3.177.1",
            "Origin": "https://en.onlinesoccermanager.com",
            "Connection": "keep-alive",
            "Referer": "https://en.onlinesoccermanager.com/",
        }
        giocatori = (session.get("https://web-api.onlinesoccermanager.com/api/v1/leagues/" +  LeagueId+ "/teams/"+ TeamId +"/players", headers=headers).text)
        if giocatori == "":
            login(User, Pwd)
        else : break
    giocatori =  eval(giocatori.replace("true", "True").replace("false", "False").replace("null", "None"))
    return giocatori

def getLineup():
    formazione = []
    for g in giocatori:
        if not g["lineup"] == 0 and not g["lineup"] > 11:
            ovr = ""
            stat = ""
            match  g["position"]:
                case 1:
                    ovr = g["statAtt"]
                case 2:
                    ovr = g["statOvr"]
                case 3:
                    ovr = g["statDef"]
                case 4:
                    ovr = g["statDef"]

            tit = {"id" : g["id"], "nome" : (g["name"]), "pos" : g["lineup"],  "ovr" : ovr, "obj" : 100, "role" : g["position"]}
            formazione.append(tit)
    with open("Lineup.json", "w") as f:
        f.write(json.dumps(formazione, indent = 4))

def TimeCheck():
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
    time = eval((session.get("https://web-api.onlinesoccermanager.com/api/v1/leagues/" + LeagueId + "/teams/" + TeamId + "/timers", headers=headers).text).replace("false", "False").replace("true", "True").replace("null", "None"))
    for i in range(0, len(time)):
        time[i]["currentTimestamp"] = datetime.fromtimestamp(time[i]["currentTimestamp"])
        time[i]["finishedTimestamp"] = datetime.fromtimestamp(time[i]["finishedTimestamp"]) 
        if time[i]["finishedTimestamp"] < datetime.now() and not "coach" in time[i]["title"] :
           print(time[i]["title"] + " has finished")
        elif time[i]["finishedTimestamp"] > datetime.now():
            if  "coach" in time[i]["title"]:
                print(time[i]["title"] + " is busy until " + str(time[i]["finishedTimestamp"]))
            elif "Your next match" in time[i]["title"]:
                print(time[i]["title"] + " will be " + str(time[i]["finishedTimestamp"]))
                if ((time[i]["finishedTimestamp"] - datetime.now()).total_seconds() / 3600 < 8):
                    GetTrained()
                    giocatori = getTeam()
                    lineup = ""
                    with open("Lineup.json", "r") as f:
                        lineup = json.loads(f.read())
                    for g in giocatori:
                        if g["lineup"] == 0:
                            for l in lineup:
                                if l["id"] == g["id"]:
                                    payload = "lineup=" + str(l["pos"])
                                    data = session.put("https://web-api.onlinesoccermanager.com/api/v1/leagues/" + LeagueId + "/teams/" + TeamId + "/players/"+ str(l["id"]) +"/lineup", headers=headers, data=payload)
                                    break
                else:
                    lineup = ""
                    with open("Lineup.json", "r") as f:
                        lineup = json.loads(f.read())
                    best = [{"ovr" : 99, "id" : 0, "role" : 1}, {"ovr" : 99, "id" : 0, "role" : 2}, {"ovr" : 99, "id" : 0, "role" : 3}, {"ovr" : 99, "id" : 0, "role" : 4}]
                    for g in lineup:
                        match g["role"]:
                            case 1:
                                if g["obj"] - g["ovr"] < best[0]["ovr"]:
                                    best[0]["ovr"] = int(g["ovr"] - g["obj"])
                                    best[0]["id"] = g["id"]
                            case 2:
                                if int(g["ovr"])  - int(g["ovr"]) < best[1]["ovr"]:
                                    best[1]["ovr"] = int(g["ovr"] - g["obj"])
                                    best[1]["id"] = g["id"]
                            case 3:
                                if int(g["ovr"])  - int(g["ovr"]) < best[2]["ovr"]:
                                    best[2]["ovr"] = g["ovr"] - g["obj"]
                                    best[2]["id"] = g["id"]
                            case 4:
                                if int(g["ovr"])  - int(g["ovr"]) < best[3]["ovr"]:
                                    best[3]["ovr"] = int(g["ovr"] - g["obj"])
                                    best[3]["id"] = g["id"]
                    for b in best:
                        Train(b["id"], b["role"])                     

def Train(playerId : int, position : int):
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
    
    payload = "playerId=" + str(playerId) + "&trainer=" + str(position) + "&timerGameSettingId=20"
    data = session.post("https://web-api.onlinesoccermanager.com/api/v1/leagues/" + LeagueId + "/teams/" + TeamId + "/trainingsessions", headers=headers, data=payload)
    if data.status_code == 200:
        print("Training started")
    else:
        print("Trainer is busy with another player")
    
def GetTrained():
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
    data = session.get("https://web-api.onlinesoccermanager.com/api/v1/leagues/"+ LeagueId +"/teams/" + TeamId + "/trainingsessions/ongoing", headers=headers).text
    if data == "":
        return 0    
    data = eval((data).replace("false", "False").replace("true", "True").replace("null", "None"))
    for n in data:
        if datetime.fromtimestamp(n["countdownTimer"]["finishedTimestamp"]) < datetime.now():
            print(n["countdownTimer"]["title"] + " finished")
            data = session.put("https://web-api.onlinesoccermanager.com/api/v1/leagues/"+ LeagueId +"/teams/" + TeamId + "/trainingsessions/" + str(n["id"]) + "/claim", headers = headers)

#sistemare
def getChampionship():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/113.0',
        'Accept': 'application/json; charset=utf-8',
        'Accept-Language': 'en-GB, en-GB',
        'Content-Type': 'multipart/mixed; boundary=batch_dd694023-1aeb-4e90-a7a6-ce16436f1040',
        'PlatformId': '11',
        'AppVersion': '3.179.0',
        'Authorization': 'Bearer ' + access_token,
        'Origin': 'https://en.onlinesoccermanager.com',
        'Connection': 'keep-alive',
        'Referer': 'https://en.onlinesoccermanager.com/',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-site',
    }
    team = eval(((session.get("https://web-api.onlinesoccermanager.com/api/v1.1/users/" + userId + "?fields=Gdpr%2CEmail%2CTeamSlots%2CImages%2CStats", headers=headers)).text).replace("false", "False").replace("true", "True").replace("null", "None"))["teamSlots"]
    TeamList = []
    i = 0
    for t in team:
        if "team" in t:
            i += 1
            TeamList.append({"TeamId" : str(t["team"]["id"]), "LeagueId" : str(t["league"]["id"])})
            print(str(i) +". " +t["team"]["name"])

    print("Select team...")
    select = int(input())
    global TeamId
    global LeagueId
    TeamId = TeamList[select - 1]["TeamId"]
    LeagueId = TeamList[select - 1]["LeagueId"]

    print()


StartUp()
dataSession = ""
with open("Session.json", "r") as f:
    dataSession = json.load(f)
if dataSession == "{}":
    login(User, Pwd)
elif not "cookies" in dataSession.keys() or not "access_token" in dataSession.keys() or  not "refresh_token" in dataSession.keys() or not "userId" in dataSession.keys():
    login(User, Pwd)
else:
    print("Session found!")
    for cookie in dataSession["cookies"]:
        session.cookies.set(cookie['name'], cookie['value'])
    access_token = dataSession["access_token"]
    refreshtoken = dataSession["refresh_token"]
    userId = dataSession["userId"]
getChampionship()
giocatori = getTeam()
#getLineup()
while 1:
    #login(User, Pwd)
    TimeCheck()
    sleep(600)
print()


