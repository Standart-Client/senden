"""
Dies ist der Standard-Client zur Berechnung von Matrizen.
Er bekommt eine Nachricht via xmpp, die eine Zeile und eine Spalte einer Matrix enthalten.
Diese werden verrechnet und das Ergebnis zurückgeschickt.

Programmiert von Hannes Simon, Henrik Rosenberg und Phillip Kleemann

"""





#zunächst werden die Bibliotheken iportiert
import sys
import logging
import getpass
from optparse import OptionParser
import subprocess
import sleekxmpp



# set default encoding to utf8
if sys.version_info < (3, 0):
    reload(sys)
    sys.setdefaultencoding('utf8')
else:
    raw_input = input



#hier wird die Klasse definiert
class rechner(sleekxmpp.ClientXMPP):

    #Bei Erstellung des Objekts:
    def __init__(self, jid, password):
        sleekxmpp.ClientXMPP.__init__(self, jid, password)
        #fuers Debugging
        #print("init wird ausgeführt")
        #Die Session wird gestartet
        self.add_event_handler("session_start", self.start)
        # message handler
        self.add_event_handler("message", self.message)
        #Rechnungs-handler
        self.add_event_handler("multzs", self.multzs)


    #Zum Starten der Session
    def start(self, event):
        self.send_presence()
        self.get_roster()
        #Ausgabe der Info des erfolgreichen Starts
        print("startet")


    #Zum multiplizieren von einer Zeile mit einer Spalte
    def multzs(self, z, s):
        zm=len(z) 
        sn=len(s)
        #Hier wird überprüft ob die Multiplikation ausführbar ist
        if zm != sn: 
            print('Spalten der Matrix (',zm,') ungleich Zeilen des Vektors (',sn,')')
            ergebnis = "Fehler"
        else:
            #Wenn es rechenbar ist:
            ergebnis=0
            #Nun wird gerechnet
            for j in range(zm): 
                ergebnis += z[j]*s[j]
            #Das Ergebnis wird zum versenden formatiert
            send = "result;" + str(z)+","+str(s)+","+str(ergebnis)
            #und zurückgegeben
            return send    

        
    #Wenn eine Nachricht empfangen wird:
    def message(self, msg):
        #Der Absender wird ermittelt
        #und neu formatiert
        a = str(msg['from'])
        try:
            b = a.split("/")
            del b[-1]
            absender = b[0]
        except:
            absender = str(msg['from'])

        #Die Nachricht und der Absender werden ausgegeben:
        print(absender + ": " +msg['body'])
        #Die nachricht wierd in der Variable nachricht gespeichert
        nachricht = msg['body']
        #Hier wird dann die Nachricht so aufgesplitted, dass sie verrechnet werden kann
        nachricht.split(";") 
        xz = nachricht.split(":")[0] 
        xs = nachricht.split(":")[1] 
        nz = xz.split(";")[0] 
        ns = xs.split(";")[0] 
        z = [float(i) for i in xz.split(";")[1].split(",")] 
        s = [float(i) for i in xs.split(";")[1].split(",")]
        #Die Zahlen werden an die Rechenfunktion übergeben
        #Das Ergebnis kommt dann in die Variable antwort
        antwort = self.multzs(z, s)
        #Das Ergebnis wird an den Absender zurückgeschickt
        self.send_message(absender, antwort)


#Das hier ist auch für irgendwas wichtig
if __name__ == '__main__':
    # Setup the command line arguments.
    optp = OptionParser()

    # Output verbosity options.
    optp.add_option('-q', '--quiet', help='set logging to ERROR',
                    action='store_const', dest='loglevel',
                    const=logging.ERROR, default=logging.INFO)
    optp.add_option('-d', '--debug', help='set logging to DEBUG',
                    action='store_const', dest='loglevel',
                    const=logging.DEBUG, default=logging.INFO)
    optp.add_option('-v', '--verbose', help='set logging to COMM',
                    action='store_const', dest='loglevel',
                    const=5, default=logging.INFO)

    
    opts, args = optp.parse_args()

    # Setup logging.
    logging.basicConfig(level=opts.loglevel,
                        format='%(levelname)-8s %(message)s')

    #Hier wird der Username und das Passwort abgefragt
    username = input("Username: ")
    passwort = input("Password: ")
    opts.jid = username +'@ifga'
    opts.password = passwort
    #Ausgabe des Logins
    print("Logged in as " + opts.jid)


    #nun wird das Objekt aus der Klasse erzeugt und die Plugins werden eingebunden
    rechner = rechner(opts.jid, opts.password)
    rechner.register_plugin('xep_0030') # Service Discovery
    rechner.register_plugin('xep_0004') # Data Forms
    rechner.register_plugin('xep_0060') # PubSub
    rechner.register_plugin('xep_0199') # XMPP Ping
    #Damit nachrichten aller User empfangen werden können
    rechner.auto_authorize = True
    rechner.auto_subscribe = True

    # Die Verindung wird aufgebaut
    if rechner.connect(('corvi.dd-dns.de', 5222), use_tls=False): #Kein SSL Zertifikat Error
        rechner.process(threaded=False) #block=True
        #bei erfolgreicher Verbindung wird dies gemeldet
        print("Verbunden")
    else:
        #ansonsten gibt es eine Fehlermeldung:
        print("Verbindungsfehler")
    
