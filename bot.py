import requests
import json
import time
from colorama import init, Fore, Style

init()

merah = Fore.LIGHTRED_EX
putih = Fore.LIGHTWHITE_EX
hijau = Fore.LIGHTGREEN_EX
kuning = Fore.LIGHTYELLOW_EX
biru = Fore.LIGHTBLUE_EX
reset = Style.RESET_ALL

banner = f"""
    {putih}AUTO Claim {hijau}GLEAM 
    
    {putih}By: {hijau}qyzan
    {putih}Github: {hijau}https://github.com/qyzan
    
    {hijau}Message: {putih}Dont Forget To Claim Every Day
"""
print(banner)

def read_file(file_path):
    with open(file_path, 'r') as file:
        return file.read().strip()

def read_json_file(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

payloads = read_json_file('payload.json')
cookies = read_file('cookies.txt').splitlines()

def countdown(seconds):
    while seconds > 0:
        hours, remainder = divmod(seconds, 3600)
        minutes, seconds_left = divmod(remainder, 60)
        print(f"Next in: {hours:02}:{minutes:02}:{seconds_left:02}", end="\r")
        time.sleep(1)
        seconds -= 1
    print()

def login(payload, cookie):
    headers = {
        "Sec-Ch-Ua": '"Not/A)Brand";v="8", "Chromium";v="126"',
        "Ngrok-Skip-Browser-Warning": "69420",
        "Accept-Language": "en-US",
        "Cookie": cookie,
        "Sec-Ch-Ua-Mobile": "?0",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.6478.57 Safari/537.36",
        "Content-Type": "application/json",
        "Accept": "application/json, text/plain, */*",
        "Sec-Ch-Ua-Platform": '"Windows"',
        "Origin": "https://app.gleam.bot",
        "Sec-Fetch-Site": "same-site",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Dest": "empty",
        "Referer": "https://app.gleam.bot/",
        "Accept-Encoding": "gzip, deflate, utf-8",
        "Priority": "u=1, i"
    }

    url = "https://prod-api.gleam.bot/api/v1/accounts/auth"
    response = requests.post(url, headers=headers, data=json.dumps(payload))

    if response.status_code == 200:
        data = response.json()
        username = data['account']['username']
        id = data['account']['id']
        referal = data['account']['referralCode']
        for balance in data['balances']:
            if balance['currency'] == 'GLEAM':
                amount_gleam = float(balance['amount'])
                break

        print(f'{putih}-'*80)
        print(f"{hijau}Id User : {putih}{id}")
        print(f"{hijau}Login as : {putih}{username}")
        print(f"{hijau}Balance GLEAM : {putih}{amount_gleam}")
        print(f'{hijau}Referal Code : {putih}{referal}')

        return response.json().get('token'), headers
    else:
        raise Exception("Failed to obtain authorization token")

def CheckEnergy(auth_token, headers, payload):
    headers["Authorization"] = f"Bearer {auth_token}"

    url_claim = "https://prod-api.gleam.bot/api/v1/accounts/energy/refill/claim"
    url_start = "https://prod-api.gleam.bot/api/v1/accounts/energy/refill/start"

    new_payload = {
        "initData": payload['initData']
    }

    claim = requests.post(url=url_claim, headers=headers, json=new_payload)
    start = requests.post(url=url_start, headers=headers, json=new_payload)

    if claim.status_code == 200:
        print(f"{hijau}Success to Claim Energy : {putih}{claim.status_code}")
    if start.status_code == 200:
        print(f"{hijau}Success to Start Energy : {putih}{start.status_code}")
    else:
        print(f'{merah}Energi Sedang Proses Refill {claim.status_code}')
    return claim.status_code

def checkProject(auth_token, headers):
    headers["Authorization"] = f"Bearer {auth_token}"
    url = 'https://prod-api.gleam.bot/api/v1/projects/list'
    
    response = requests.get(url, headers=headers)
    data = response.json()
    slugs = [project.get('slug') for project in data.get('projects', [])]
    return slugs

def quest(auth_token, headers, payload, slugs):
    headers["Authorization"] = f"Bearer {auth_token}"
    new_payload = {
        "initData": payload['initData']
    }

    for project in slugs:
        url = f'https://prod-api.gleam.bot/api/v1/projects/{project}/quests'
        print(f'{putih}-'*80)
        print(f'{hijau}Start Quest {project} ......')
        countdown(3)
        a = requests.get(url, headers=headers)
        if a.status_code == 200:
            json_data = a.json()
            quest_ids = [quest['id'] for quest in json_data.get('quests', [])]
            for quest_id in quest_ids:
                url_check = f"https://prod-api.gleam.bot/api/v1/quests/{quest_id}/check"
                url_start = f"https://prod-api.gleam.bot/api/v1/quests/{quest_id}/start"
                url_claim = f"https://prod-api.gleam.bot/api/v1/quests/{quest_id}/claim"
                
                response = requests.post(url=url_start, headers=headers, json=new_payload)
                data = response.json()
                message = data.get('message')
                if response.status_code == 200:
                    start = requests.post(url=url_check, headers=headers, json=new_payload)
                    if start.status_code == 200:
                        title = data['quest']['title']
                        print(f'{hijau}Success to Start Quest : {putih}{title} - {start.status_code}')
                    claim = requests.post(url=url_claim, headers=headers, json=new_payload)
                    if claim.status_code == 200:
                        title = data['quest']['title']
                        print(f'{hijau}Success to Claim Quest : {putih}{title} - {claim.status_code}')
                    print(f'{putih}-'*80)

                elif message == "Insufficient energy." :
                    print(f'{putih}-'*80)
                    print(f'{merah}Energi Habis Bro..')
                    status = CheckEnergy(auth_token, headers, payload)
                    if status == 200:
                        continue
                    else:
                        return 0
                elif message == 'This quest has already been processed or completed.':
                    print(f'{biru}This quest has already been processed or completed.')
                    print(f'{hijau}Next Request....')
                    continue
                else:
                    print(response.status_code)
                    continue

def claim(auth_token, headers, payload, slugs):
    headers["Authorization"] = f"Bearer {auth_token}"
    new_payload = {
        "initData": payload['initData']
    }

    for project in slugs:
        url = "https://prod-api.gleam.bot/api/v1/projects/{project}/farming/claim"
        print(f'{putih}-'*80)
        print(f'{hijau}Start Claim Gleam in Project{project} ......')
        countdown(3)
        claim = requests.post(url=url , json=new_payload, headers=headers)
        if claim.status_code == 200:
            print(f'{hijau}Success Claim Gleam {project} ......')
        else:
            print(f'{merah}Failed to Claim Gleam / Wait until 8 hours {project} ......')

while True:
    try:
        for payload, cookie in zip(payloads, cookies):
            # Login and obtain token, headers
            token, headers = login(payload, cookie)

            # Fetch project slugs
            slugs = checkProject(token, headers)

            # Perform quests
            quest(token, headers, payload, slugs)
            print(f'{putih}-'*80)
            print(f'{hijau}Next Account....')
        print(f'{putih}-'*80)
        print(f'{kuning}Semua Account Sudah Di Proses....')
        print(f'{hijau}Refill Energy....')
        print(f'{putih}-'*80)
        print(f'{hijau}Jangan Lupa Cek Gleamnya..')
        countdown(10800)
        claim(token, headers, payload, slugs)

    except Exception as e:
        print(f'Error: {str(e)}')
