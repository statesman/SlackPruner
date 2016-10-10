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


if __name__ == '__main__':
    totalfiles = 0
    userfailures = []
    sizedeleted = 0
    for apikey in apikeys:
        userfiles = 0
        user = apikey[0]
        _token = apikey[1]
        print("Beginning to work on files of " + user)
        processedfiles = []
        done = False
        while not done:
            files_list_url = 'https://slack.com/api/files.list'
            date = str(calendar.timegm((datetime.now() + timedelta(daystoretain * -1)).utctimetuple()))
            data = {"token": _token, "ts_to": date}
            response = requests.post(files_list_url, data=data)
            if len(response.json()["files"]) == 0:
                done = True
                break
            for f in response.json()["files"]:
                if f["id"] in processedfiles:   # If this isn't our first pass through
                    print("We have problems deleting files for " + user + ". User may need admin access.")
                    userfailures.append(user)
                    userfiles = 0   # If we had one error, we probably didn't delete any files for the user
                    done = True
                    break
                processedfiles.append(f["id"])
                print("\tDeleting " + user + "'s file " + f["name"].encode("utf-8") + "...")
                timestamp = str(calendar.timegm(datetime.now().utctimetuple()))
                delete_url = "https://" + _domain + ".slack.com/api/files.delete?t=" + timestamp
                deleteresponse = requests.post(delete_url, data={
                    "token": _token,
                    "file": f["id"],
                    "set_active": "true",
                    "_attempts": "1"})
                if deleteresponse.json()["ok"]: # If we get ok: True
                    userfiles += 1
                    sizedeleted += f["size"]
                else:
                    print("\t\tError found: " + deleteresponse.json()["error"])

        totalfiles += userfiles
        print("DONE! ... with " + user + ". User files deleted: " + str(userfiles) + ". Total files deleted: " + str(totalfiles) + ".")
    print(str(totalfiles) + " files may have been deleted.")
    print("{:,}".format(sizedeleted) + " bytes may have been freed up.")
    if len(userfailures) > 0:
            print("\nWe had problems deleting files for some users: " + "; ".join(map(str, userfailures)) + ".")
