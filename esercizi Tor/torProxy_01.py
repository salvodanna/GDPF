import stem.process
import requests
import json
from datetime import datetime

proxies = {
    'http':'socks5://127.0.0.1:9050',
    'https':'socks5://127.0.0.1:9050'
}

def print_tor_ip_info():
    response = requests.get('http://ip-api.com/json/', proxies=proxies)
    result = json.loads(response.content)
    #print(result)
    print('TOR IP [%s]: %s %s %s' % (datetime.now().strftime("%d-%m-%Y %H:%M:%S"), result["query"], result["country"], result["city"]))

tor = stem.process.launch_tor(init_msg_handler=print)

print_tor_ip_info()

tor.terminate()