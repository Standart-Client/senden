
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

print("test")


class EchoBot(sleekxmpp.ClientXMPP):

    def __init__(self, jid, password):
        sleekxmpp.ClientXMPP.__init__(self, jid, password)
        print("init wird ausgeführt")
        # start the session
        self.add_event_handler("session_start", self.start)


        # message handler
        self.add_event_handler("message", self.message)
        self.add_event_handler("nachricht_senden", self.nachricht_senden)
        self.add_event_handler("multzs", self.multzs)
        
    def nachricht_senden(self):
        name = input("Name an: ")
        nachricht = input("Nachricht: ")
        self.send_message(name + "@ifga", nachricht)
        
    def start(self, event):
        # session start method
        self.send_presence()
        self.get_roster()
        print("startet")

    def multzs(self, z, s):
       zm=len(z) 
       sn=len(s) 
       if zm != sn: 
          print('Spalten der Matrix (',zm,') ungleich Zeilen des Vektors (',sn,')') 
       else: 
          ergebnis=0 
          for j in range(zm): 
             ergebnis += z[j]*s[j] 
          send = "result;" + str(z)+","+str(s)+","+str(ergebnis) 
          return send    

        

    def message(self, msg):
        a = str(msg['from'])
        try:
            b = a.split("/")
            del b[-1]
            c = b[0]
        except:
            c = str(msg['from'])
        
        print(c + ": " +msg['body'])
        m = msg['body']
        name = c
        #Hier wird dann berechnet
        m.split(";") 
        xz = m.split(":")[0] 
        xs = m.split(":")[1] 
        nz = xz.split(";")[0] 
        ns = xs.split(";")[0] 
        z = [float(i) for i in xz.split(";")[1].split(",")] 
        s = [float(i) for i in xs.split(";")[1].split(",")]
        #Die Antwort kommt dann in die Variable nachricht
        nachricht = self.multzs(z, s)
        self.send_message(name, nachricht)





            
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
    x = input("Username: ")
    y = input("Password: ")
    opts.jid = x +'@ifga'
    opts.password = y
    print("Logged in as " + opts.jid)

    # Setup the EchoBot and register plugins. Note that while plugins may
    # have interdependencies, the order in which you register them does
    # not matter.
    xmpp = EchoBot(opts.jid, opts.password)
    xmpp.register_plugin('xep_0030') # Service Discovery
    xmpp.register_plugin('xep_0004') # Data Forms
    xmpp.register_plugin('xep_0060') # PubSub
    xmpp.register_plugin('xep_0199') # XMPP Ping
    xmpp.auto_authorize = True
    xmpp.auto_subscribe = True

    # Connect to the XMPP server and start processing XMPP stanzas.
    if xmpp.connect(('odin', 5222), use_tls=False): #Kein SSL Zertifikat Error
        xmpp.process(threaded=False) #block=True
        print("Done")
    else:
        print("Unable to connect.")
    
