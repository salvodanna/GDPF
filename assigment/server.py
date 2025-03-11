import requests
from datetime import datetime, timedelta
from flask import Flask, request, jsonify

app = Flask('mio_server')

blocked_countries = ["RU", "CN", "US", "IT"]  # il server bloccherà le richieste provenienti da ip russi, cinesi, statunitensi e italiani
ip_list = list()

def get_country_ip(ip):
    try:
        #uso il servizio ipinfo.io per recuperare il paese di provenienza dell'indirizzo ip che effettua la richiesta al mio server
        access_token = "b2a56c2025df53"
        url = f"https://ipinfo.io/{ip}/json?token={access_token}"
        response = requests.get(url)
        data = response.json()
        country = data.get("country", "")
        return country
    except Exception as e:
        print(f"Errore nel recuperare la geolocalizzazione dell'IP: {e}")
        return None

@app.route('/')
def home():
    # Con la semplice request.remote_addr otteniamo sempre 127.0.0.1 poichè c'è un proxy davanti Flask,
    # quindi per ottenere l'indirizzo ip originale della richiesta ci serve guardare l'header X-Forwarded-For.
    # Tuttavia questo indirizzo sarà solo quello dell'exit node della nostra rete Tor.
    if request.headers.getlist("X-Forwarded-For"):
        print(f'X-Forwarded-For: {request.headers.getlist("X-Forwarded-For")}')
        client_ip = request.headers.getlist("X-Forwarded-For")[0]
    else:
        client_ip = request.remote_addr
    country = get_country_ip(client_ip)

    c=0
    for ip, date, first in ip_list:
        if ip==client_ip:
            c+=1
    if c == 3:  # se un indirizzo ip è presente 3 volte nella lista, controllo che siano trascorse almeno 24 ore tra la prima richiesta fatta e quella corrente
        for ip, data, first in ip_list:
            if ip == client_ip and first:
                present = datetime.now()
                print(data)
                data = datetime(data[0],data[1],data[2],data[3],data[4],data[5]) #faccio una conversione da tupla a oggetto datetime per poter fare il confronto, il formato deve essere anno/mese/giorno/ora/minuti/secondi
                past = data+timedelta(days=1)
                if present >= past:  # se sono passate almeno 24 ore, elimino tutte le occorrenze dell'indirizzo ip nella lista
                    for item in ip_list[:]: #vado a iterare su una copia della lista perché fare modifiche sulla lista mentre è in corso l'iterazione provoca comportamenti indesiderati, ovvero salta alcuni elementi
                        if item[0] == client_ip:
                            ip_list.remove(item)
                            c-=1

    if country not in blocked_countries and c<3:
        d = datetime.now().year, datetime.now().month,datetime.now().day,datetime.now().hour,datetime.now().minute,datetime.now().second
        if c==0:
            ip_list.append((client_ip, d, True)) # inserisco un flag per segnare la prima richiesta che viene effettuata da ogni indirizzo ip
        else:
            ip_list.append((client_ip, d, False))
        print(ip_list)
    elif country in blocked_countries:
        return jsonify({"error": "Accesso vietato, paese di provenienza non accettato"}), 403
    elif c==3:
        return jsonify({"error": "Accesso vietato, hai superato il limite di 3 accessi in 24 ore"}), 403

    return "<h1>Benvenuto nel mio server!</h1>"

if __name__ == '__main__':
    app.run(port=8000)
