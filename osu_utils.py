import requests
import re
import apiv2
import json

def get_user(id):
    headers = {'Authorization':'Bearer '+apiv2.getAPIKey(id, "osu")}
    oApiRequest = requests.get('https://osu.ppy.sh/api/v2/users/'+str(id), headers=headers)
    return json.loads(oApiRequest.text)