import requests
import os
import time

# 0.1 Initial version
# 0.2 Added upload ETA
# 0.3 Preparations for autorun

AUTOWIKI_USER = os.environ.get('AUTOWIKI_USER')
AUTOWIKI_PASS = os.environ.get('AUTOWIKI_PASS')

def uploadImages(renderCache:dict, rate:float, prefix=''):
    print(f'ETA: {len(renderCache.keys()) * rate} seconds')
    S = requests.Session()
    URL = "https://monolithss14.miraheze.org/w/api.php"

    HEADER = {'User-Agent' : 'MapRenderUpload/0.3 (User:Ical92 @ical)'}

    # Step 1: Retrieve a login token
    PARAMS_1 = {
        "action": "query",
        "meta": "tokens",
        "type": "login",
        "format": "json"
    }

    R = S.get(url=URL, params=PARAMS_1, headers=HEADER)
    DATA = R.json()

    LOGIN_TOKEN = DATA["query"]["tokens"]["logintoken"]

    # Step 2: Send a post request to login. Use of main account for login is not
    # supported. Obtain credentials via Special:BotPasswords
    # (https://www.mediawiki.org/wiki/Special:BotPasswords) for lgname & lgpassword
    PARAMS_2 = {
        "action": "login",
        "lgname": AUTOWIKI_USER,
        "lgpassword": AUTOWIKI_PASS,
        "format": "json",
        "lgtoken": LOGIN_TOKEN
    }

    R = S.post(URL, data=PARAMS_2, headers=HEADER)

    # Step 3: Obtain a CSRF token
    PARAMS_3 = {
        "action": "query",
        "meta":"tokens",
        "format":"json"
    }

    R = S.get(url=URL, params=PARAMS_3, headers=HEADER)
    DATA = R.json()

    CSRF_TOKEN = DATA["query"]["tokens"]["csrftoken"]

    # Step 4: Post request to upload a file directly
    for ID, FILE_PATH in renderCache.items():
        FILE_NAME = f"{prefix}Render-{ID}.png"
        PARAMS_4 = {
            "action": "upload",
            "filename": FILE_NAME,
            "format": "json",
            "token": CSRF_TOKEN
        }

        FILE = {'file':(FILE_NAME, open(FILE_PATH, 'rb'), 'multipart/form-data')}

        R = S.post(URL, files=FILE, data=PARAMS_4, headers=HEADER)
        print(f'Uploading {FILE_NAME}: ', end='')
        R.raise_for_status()
        match R.json().get('upload', {}).get('result'):
            case 'Success':
                print('Success (New Upload)')
            case 'Warning':
                warnings = R.json()['upload'].get('warnings', {})
                if warnings.get('exists') == FILE_NAME:
                    if warnings.get('nochange') and list(warnings.keys()) == ['exists', 'nochange']: # Warnings are only that it exists and there was no change
                        print('Success (No Change)')
                        continue
                    if list(warnings.keys()) == ['exists']: # Warnings are only that it exists
                        time.sleep(rate)
                        PARAMS_5 = {
                            "action": "upload",
                            "filename": FILE_NAME,
                            "format": "json",
                            "token": CSRF_TOKEN,
                            "filekey": R.json()['upload']['filekey'],
                            "ignorewarnings": 1
                        }
                        R = S.post(URL, data=PARAMS_5, headers=HEADER)
                        R.raise_for_status()
                        print('Success (Updated File)')
                        continue
                print(f'Success (With warnings: {warnings})') # Some other warnings occured
            case _:
                print('Failed:', R.content)
                break
        time.sleep(rate)
