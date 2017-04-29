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

# For each apikey, we need to get the user_id from auth.text, and then check for owner or administrative privileges from
# users.info. If we don't have elevated access, we need to filter files.list by files owned just by that user.
# If we do have elevated access, we don't filter files.list.

if __name__ == '__main__':
    totalfiles = 0
    userfailures = []
    sizedeleted = 0
    baseurl = "https://" + _domain + ".slack.com/api/"
    for apikey in apikeys:
        userfiles = 0
        user = apikey[0]
        _token = apikey[1]
        print("Beginning to work on files of " + user)
        apitest_data = {"token": _token}
        apitest_response = requests.post(baseurl + "auth.test", data=apitest_data)
        try:
            user_id = apitest_response.json()["user_id"]
            usersinfo_data = {"token": _token, "user": user_id}
            usersinfo_response = requests.post(baseurl + "users.info", data=usersinfo_data)
            userinfo = usersinfo_response.json()["user"]
            if userinfo["is_admin"] or userinfo["is_owner"]:
                print(user + " has elevated powers. Searching for all files available.")
                elevated = True
            else:
                elevated = False
            processedfiles = []
            done = False
            while not done:
                date = str(calendar.timegm((datetime.now() + timedelta(daystoretain * -1)).utctimetuple()))
                fileslist_data = {"token": _token, "ts_to": date}
                if not elevated:
                    fileslist_data['user'] = user_id    # If not admin or owner, limit search to that user's files
                list_response = requests.post(baseurl + "files.list", data=fileslist_data)
                if len(list_response.json()["files"]) == 0:
                    done = True
                    break
                for f in list_response.json()["files"]:
                    if f["id"] in processedfiles:   # If this isn't our first pass through
                        print("We have problems deleting files for " + user + ". User may need admin access.")
                        userfailures.append(user)
                        userfiles = 0   # If we had one error, we probably didn't delete any files for the user
                        done = True
                        break
                    processedfiles.append(f["id"])
                    # print("\tDeleting " + user + "'s file " + f["name"].encode("utf-8") + "...")
                    # print(str(f["name"]))
                    print("\tDeleting " + user + "'s file " + str(f["name"].encode("utf-8")) + " ...")
    # Traceback (most recent call last):
    #  File "C:\data\SlackPruner\pruner.py", line 61, in <module>
    #    print(("\tDeleting " + user + "'s file " + f["name"].encode("utf-8") + "...").encode("utf-8"))
    # TypeError: must be str, not bytes
                    timestamp = str(calendar.timegm(datetime.now().utctimetuple()))
                    delete_url = baseurl + "files.delete?t=" + timestamp
                    delete_data = {
                        "token": _token,
                        "file": f["id"],
                        "set_active": "true",
                        "_attempts": "1"
                        }
                    deleteresponse = requests.post(delete_url, data=delete_data)
                    if deleteresponse.json()["ok"]: # If we get ok: True
                        userfiles += 1
                        sizedeleted += f["size"]
                    else:
                        print("\t\tError found: " + deleteresponse.json()["error"])
            totalfiles += userfiles
        except:
            print("*******************************************")
            print("There may have been a problem with " + user)
            print("*******************************************")
        print("DONE! ... with " + user + ". User files deleted: " + str(userfiles) + ". Total files deleted: " + str(totalfiles) + ".")
    print(str(totalfiles) + " files may have been deleted.")
    print("{:,}".format(sizedeleted) + " bytes may have been freed up.")
    if len(userfailures) > 0:
            print("\nWe had problems deleting files for some users: " + "; ".join(map(str, userfailures)) + ".")
