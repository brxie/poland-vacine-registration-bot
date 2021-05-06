#!/usr/bin/python3
import requests
import datetime
from time import sleep

COOKIE_SID = '044abd74-84ea-4e84-ab95-1e82ee83c895'
CSRF_TOKEN = 'c945c014-9dd1-48fa-976e-073de8a08730'
PRESCIPTION_ID = 'de2cb866-c9fb-4979-8464-c685377cce7d'
API_URL = 'https://pacjent.erejestracja.ezdrowie.gov.pl/api'
BACKOFF_TIME = 0.1
vacines = ["cov19.pfizer"] # vaccines to be included in query
provinces = {"małopolskie": 12, "świętokrzyskie": 26, "śląskie": 24} # TERYT ids to be included in query. Full list https://pl.wikipedia.org/wiki/Wojew%C3%B3dztwo
AUTO_REGISTER = False

payload = {
    "dayRange": {
        "from": "2021-05-08",
        "to": "2021-05-09"
    },
    "prescriptionId": PRESCIPTION_ID,
    "voiId": None,
    "vaccineTypes": vacines
}


s = requests.Session()
cookies = {'patient_sid': COOKIE_SID}
s.headers.update({'content-type': 'application/json'})
s.headers.update({'authority': 'pacjent.erejestracja.ezdrowie.gov.pl'})
s.headers.update({'sec-fetch-dest': 'empty'})
s.headers.update({'sec-fetch-mode': 'cors'})
s.headers.update({'x-csrf-token': CSRF_TOKEN})
s.headers.update({'origin': 'https://pacjent.erejestracja.ezdrowie.gov.pl'})
s.headers.update({'user-agent': 'Mozilla/5.0'})


while True:
    print('.', end='', flush=True)
    for provName, provId in provinces.items():

        payload['voiId'] = str(provId)

        resp = s.post(API_URL + '/calendarSlots/find', json=payload, cookies=cookies)
        if resp.status_code != 200:
            print("Unexpected response code: %d, %s" % (resp.status_code, resp.text))
            exit(1)

        if not 'list' in resp.json(): continue

        for slot in resp.json()['list']:
            startAt = datetime.datetime.strptime(slot['startAt'], '%Y-%m-%dT%H:%M:%SZ')
            print("\n------------------------------------------------")
            print("punkt: %s" % slot['servicePoint']['name'])
            print("adres: %s" % slot['servicePoint']['addressText'])
            print("szczepionka: %s" % slot['vaccineType'])
            print("województwo: %s" % provName)
            print("data: %s" % startAt.strftime('%A, %d %b %H:%M:%S +0000'))
            
            if AUTO_REGISTER:
                resp = s.post('%s/calendarSlot/%s/confirm' % (API_URL, slot['id']),
                            json={"prescriptionId": PRESCIPTION_ID},
                            cookies=cookies)
                if resp.status_code != 200:
                    print("Can't register: %d, %s" % (resp.status_code, resp.text))
                    exit(1)
                print("Sucesfully registered! %s" % resp.text)
            exit(0)
    sleep(BACKOFF_TIME)
