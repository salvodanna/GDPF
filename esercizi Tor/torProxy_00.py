# poichè stiamo creando un processo Tor, dobbiamo stoppare il demone Tor
# già in esecuzione con il comando
# sudo /etc/init.d/tor stop
import stem.process

# init_msg_handler ci consente di specificare la funzione che gestirà i messaggi
#riguardanti l'inizializzazione di Tor
tor = stem.process.launch_tor(init_msg_handler=print)

tor.terminate()