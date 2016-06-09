import requests
import json
import calendar
from datetime import datetime, timedelta
from sys import exit
import creds    # You need to set your configuration in creds.py. And please read all the warnings.

# Configure creds.py for this to work.
_domain = creds.setup['domain']
daystoretain = creds.setup['daystoretain']
apikeys = creds.setup['apikeys']

if apikeys[0][1] == "xoxp-1234567890-1234567890-1234567890-1234567890":
    print("You need to configure creds.py for this to work.")
    exit()

class QuitProcessingUser( Exception ):
    pass

if __name__ == '__main__':
    totalfiles = 0
    for apikey in apikeys:
        userfiles = 0
        name = apikey[0]
        _token = apikey[1]
        print("Beginning to work on files of " + name)
        firstfile = "ireallyhateslackrightnow"
        done = False
        while not done:
            files_list_url = 'https://slack.com/api/files.list'
            date = str(calendar.timegm((datetime.now() + timedelta(daystoretain * -1)).utctimetuple()))
            data = {"token": _token, "ts_to": date}
            response = requests.post(files_list_url, data = data)
            if len(response.json()["files"]) == 0:
                done = True
                break
            for f in response.json()["files"]:
                if firstfile == "ireallyhateslackrightnow":
                    firstfile = f["id"]
                if firstfile == f["id"] and userfiles > 0:   # If this isn't our first pass through
                    print("We have problems deleting files for " + name + ". User may need admin access.")
                    done = True
                    break
                print("\tDeleting " + name + "'s file " + f["name"].encode("utf-8") + "...")
                timestamp = str(calendar.timegm(datetime.now().utctimetuple()))
                delete_url = "https://" + _domain + ".slack.com/api/files.delete?t=" + timestamp
                requests.post(delete_url, data = {
                    "token": _token, 
                    "file": f["id"], 
                    "set_active": "true", 
                    "_attempts": "1"})
                userfiles += 1

        totalfiles += userfiles
        print("DONE! ... with " + name + ". User files deleted: " + str(userfiles) + ". Total files deleted: " + str(totalfiles) + ".")
