import requests
import json
from datetime import datetime, date, time, timedelta

expiration_timer = 0
timer_last_queried = datetime.now()
auth_code = None

def getAPIKey(id, mode):
    global expiration_timer, timer_last_queried, auth_code
    if getExpirationDate() < datetime.now():
        payload = {'client_id':1672, 'client_secret':'token', 'grant_type':'client_credentials', 'scope':'public'}
        oRequest = requests.post('https://osu.ppy.sh/oauth/token', data=payload)
        colResponse = oRequest.json()
        headers = {'Authorization':'Bearer token'}
        oApiRequest = requests.get('https://osu.ppy.sh/api/v2/users/'+str(id)+'/'+str(mode), headers=headers)
        expiration_timer = int(colResponse['expires_in'])
        timer_last_queried = datetime.now()
        auth_code = colResponse['access_token']
    return auth_code

def addSecs(tm, secs):
    fulldate = datetime(100, 1, 1, tm.hour, tm.minute, tm.second)
    fulldate = fulldate + timedelta(seconds=secs)
    return fulldate.time()

def getExpirationDate():
    return timer_last_queried + timedelta(seconds=expiration_timer) - timedelta(seconds=1000)