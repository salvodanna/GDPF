import stem.process
import requests
import json
from datetime import datetime
import time

from stem import CircStatus
from stem.control import Controller

proxies = {
    'http':'socks5://127.0.0.1:9050',
    'https':'socks5://127.0.0.1:9050'
}

def print_tor_ip_info():
    response = requests.get('http://ip-api.com/json/', proxies=proxies)
    result = json.loads(response.content)
    #print(result)
    print('TOR IP [%s]: %s %s %s' % (datetime.now().strftime("%d-%m-%Y %H:%M:%S"), result["query"], result["country"], result["city"]))

CONTROL_PORT = 9051
tor = stem.process.launch_tor_with_config(
    config = {
        'EntryNodes':'{US}',
        'ExitNodes':'{DE}',
        'MaxCircuitDirtiness':'10',
        'ControlPort': str(CONTROL_PORT),
        'CookieAuthentication':'1',
    }, init_msg_handler=print
)

print_tor_ip_info()
#https://stem.torproject.org/api/control.html
with Controller.from_port(port=CONTROL_PORT) as controller:
    controller.authenticate()
    #vediamo tutti i circuiti
    for x in controller.get_circuits():
        print(x)

    for circ in sorted(controller.get_circuits()):
        if circ.status == CircStatus.BUILT:
            print("Circuit %s (%s)" % (circ.id, circ.purpose))

            for i,entry in enumerate(circ.path):
                # segno con + l'exit node
                div = '+' if (i==len(circ.path)-1) else '|'
                fingerprint, nickname  = entry
                desc = controller.get_network_status(fingerprint, None)
                address = desc.address if desc else 'unknown'
                print(" %s- %s (%s,%s)" % (div, fingerprint, nickname, address))

    tor.terminate()