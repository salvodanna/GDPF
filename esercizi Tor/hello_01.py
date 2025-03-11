import requests
import time
from stem import Signal
from stem.control import Controller

proxies = {
    'http':'socks5://127.0.0.1:9050',
    'https':'socks5://127.0.0.1:9050'
}

print(requests.get('https://ident.me').text)

for i in range(5):
    print(requests.get('https://ident.me', proxies=proxies).text)

    # rinnovo indirizzo IP
    with Controller.from_port(port=9051) as controller:
        controller.authenticate(password="monello")
        # forza la creazione di un nuovo circuit
        controller.signal(Signal.NEWNYM)
    time.sleep(5)
