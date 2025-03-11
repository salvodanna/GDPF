import requests
import time
from stem import Signal
from stem.control import Controller
import json
from datetime import datetime

proxies = {
    'http':'socks5://127.0.0.1:9050',
    'https':'socks5://127.0.0.1:9050'
}

print(requests.get('https://ident.me').text)

def print_tor_ip_info():
    response = requests.get('http://ip-api.com/json/', proxies=proxies)
    result = json.loads(response.content)
    print(result)
    print('TOR IP [%s]: %s %s %s' % (datetime.now().strftime("%d-%m-%Y %H:%M:%S"), result["query"], result["country"], result["city"]))

for i in range(5):
    print_tor_ip_info()
    print(requests.get('https://ident.me', proxies=proxies).text)

    # rinnovo indirizzo IP
    with Controller.from_port(port=9051) as controller:
        controller.authenticate(password="monello")
        # forza la creazione di un nuovo circuit
        controller.signal(Signal.NEWNYM)
    time.sleep(5)
