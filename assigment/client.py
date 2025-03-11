import stem.process
import requests
import time
from stem import CircStatus
from stem.control import Controller

proxies = {
    'http':'socks5://127.0.0.1:9050',
    'https':'socks5://127.0.0.1:9050'
}

ngrok_url = 'https://5014-79-23-160-214.ngrok-free.app'
# utilizzo ngrok per creare un tunnel in modo da rendere il mio server raggiungibile da Internet, ovvero il traffico indirizzato a questo URL viene reindirizzato a localhost:8000
# dopo aver eseguito il comando 'ngrok http 8000' il link ottenuto sarà ngrok_url
def print_tor_ip_info():
    response = requests.get(ngrok_url, proxies=proxies)

c=0
while c<20: # effettuo un certo numero di richieste al server per verificare se riesco ad aggirare i controlli in modo efficace
    CONTROL_PORT = 9051
    tor = stem.process.launch_tor_with_config(
        config = {
            'EntryNodes':'{RU},{CN},{US},{IT}', # effettuo la richiesta dai paesi non accettati
            'ExcludeExitNodes':'{RU},{CN},{US},{IT}', #escludo i paesi non accettati dal server dai nodi di uscita
            'MaxCircuitDirtiness':'5', # ogni 5 secondi viene creato un nuovo percorso
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
        c += 1
        print(c)
        tor.terminate()
        time.sleep(5) # metto una sleep per dare il tempo di terminare il processo corrente prima di creare il successivo
