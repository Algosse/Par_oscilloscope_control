"""
Ce fichier est une bibliothèque écrite dans le cadre du PAr123 à l'Ecole Centrale de Lyon (année 2020/2021) et portant sur la réalisation d'une interface permettant de mener de façon automatique des attaques par canaux
electromagnétiques à l'aide d'une imprimante 3D.
Il contient la classe communication_serie écrite pour la gestion de la communication série avec l'imprimante 3D.
Le fonctionnement général est le suivant : à l'instanciation (après avoir branché l'imprimante et vérifié que le port est le bon) on crée deux threads qui vont fonctionner
en parallèle : un thread d'envoie de commandes à l'imprimante (il va pointer sur _sender qui va envoyer les commandes rajoutées à la file self.queue) et un thread de lecture
des retours de l'imprimante, qui sera in fine utile principalement pour le debbuging (pour s'assurer que l'imprimante est bien connectée par exemple).

Ce fichier est utilisé (importé) par la suite dans le main.py qui rassemble les fonctions utilisées par l'interface graphique (crée dans le fichier Oscilloscope_control.py). 

L'écriture de ce fichier s'est inspirée des codes open source du logiciel d'impression 3D Printrun.

Dimitri Le Foll, mars 2021
"""

from serial import Serial, PARITY_ODD, PARITY_NONE # documentation : https://pyserial.readthedocs.io/en/latest/pyserial_api.html
from queue import Queue, Empty as QueueEmpty # documentation : https://docs.python.org/fr/3/library/queue.html
import threading #un thread est un fil d'exécution (objet Thread) qui permet la mise en parallèle de plusieurs processus. On lui passe en argument un objet appelable (une fonction par exemple) que la méthode
#run() va exécuter. Si cet objet a besoin d'arguments, on lui fournit grâce à args (tuple) et kwargs (dictionnaire).
#attention, il faut décaler tout les def car il y a un pb d'indentation sinon
import errno

class communication_serie():

    def __init__(self, port = None, baud = None):
        self.baud = None #baudrate, vitesse de communication. regarder laquelle est fixée côté arduino (rappel : on est en asynchrone donc il faut la même)
        self.port = None # port de connexion (il faut regarder quel port a été attribué par windows : aller dans le gestionnaire de périphérique pour voir (arduino souvent en COM3))
        self.printer = None #contiendra l'objet serial qui sera le gestionnaire du port série côté logiciel
        self.online = False #l'imprimante a répondu à la première commande et donc la communication est établie
        #pour retirer et renvoyer un élément, on utilise la méthode publique .get(block=True, timeout=None), cf doc pour les arguments
        self.queue = Queue(0) #file des commandes à envoyer (FIFO, le 0 veut dire qu'elle est infinie)
        self.read_thread = None #futur objet Thread de lecture
        self.stop_read_thread = False #dit si le thread read_thread de lecture est vivant ou pas (False = vivant, True = mort)
        self.send_thread = None #futur objet Thread d'envoi de commandes
        self.stop_send_thread = False #dit si le thread d'envoi de commandes est vivant ou pas (False = vivant, True = mort)
        self.greetings = ['start', 'Grbl '] #ce que peuvent renvoyer certaines imprimantes quand elles reçoivent une commande d'initialisation M105

        #connexion de l'imprimante lors de l'instanciation
        if port is not None and baud is not None:
            self.connect(port, baud)

#----------------------------------------gestion de la connexion (méthodes publiques) --------------------------------------------------------------------

    def disconnect(self): #déconnecte de l'imprimante et met en pause les instructions
        if self.printer: #si on a ouvert une connexion série
            if self.read_thread: #si le thread de lecture est vivant
                self.stop_read_thread = True #on signale qu'on va le faire mourir : listen_can_continue renvoie False et on peut sortir de la boucle while du listen !
                if threading.current_thread() != self.read_thread: #si le Thread appelant est différent de self.read_thread
                    self.read_thread.join() #on stoppe le thread appelant jusqu'à ce que self.read_thread soit fini (puisqu'il est en train d'appeler cette fonction, on marque une pause ici.. en attendant de sortir du while de listen)
                self.read_thread = None #self.read_thread est sensé avoir fini, on le fait mourir en mettant None
            self._stop_sender() #on appelle cette fonction qui va faire mourir le thread d'envoi de commandes
        self.printer = None #on est déconnecté de l'immrimante


    def connect(self, port = None, baud = None):
        if self.printer: #si l'imprimante est déjà connectée, on la déconnecte
            self.disconnect()
        if port is not None:
            self.port = port
        if baud is not None:
            self.baud = baud
        if self.port is not None and self.baud is not None:
            try:
                self.printer = Serial(baudrate = self.baud, timeout = 0.25, parity = PARITY_NONE) #objet qui gère la connexion série via USB
                #parity gère le bit de parité de l'octet (contrôle d'erreurs). Ici on en a pas (windows le gère tout seul), d'où PARITY_NONE
                self.printer.port = self.port #à la création de l'objet on ne lui a pas donné de port, il faut donc lui donner ici et faire un .open()
                self.printer.open()
            except:
                print("erreur connexion à l'imprimante, programme stoppé")
                return
            print("la connexion s'est bien passée")
            self.stop_read_thread = False #thread de lecture sur le port série va devenir vivant : on le signal dans cette variable
            self.read_thread = threading.Thread(target = self._listen,name='read thread') #création du thread de lecture qui pointe sur la fction privée _listen
            self.read_thread.start() #on active le thread crée
            self._start_sender() #on lance la fonction privée _start_sender

#----------------------------------------gestion des envois de commandes (méthodes privées)--------------------------------------------------------------------
  
    def _start_sender(self): #création du thread d'envoi des commandes
        self.stop_send_thread = False #le thread d'envoi des commandes va devenir vivant, on le signale ici
        self.send_thread = threading.Thread(target = self._sender,name = 'send thread') #création du thread d'envoi des commandes : il pointe sur
        #la fonction privée _sender
        self.send_thread.start() #activation du thread d'envoi des commandes


    def _stop_sender(self):
        if self.send_thread: #si le thread d'envoi de commande est vivant
            self.stop_send_thread = True #le thread d'envoi va mourir
            self.send_thread.join() #on attend que le thread d'envoi de commande finisse en mettant en pause le thread courant
            self.send_thread = None #on supprime le thread d'envoi


    def _sender(self): #cette fonction traite au fur et à mesure la file queue de commande et fait appel à la fonction privée d'envoi _send() quand il y a quelque chose à envoyer
        while not self.stop_send_thread: #tant que le thread d'envoi est vivant
            try:
                command = self.queue.get(True, 0.1) #retire et renvoie un élément de la file ! donc une commande à envoyer à l'imprimante. True et 0.1 veulent dire que si il n'y a pas d'instruction avant 0.1 secondes, on lève une exception Empty
            except QueueEmpty: #si la file est vide
                continue #permet de sauter ce qui se passe après et passe à une itération suivante du while
            self._send(command)


    def _send(self, command, lineno = 0, calcchecksum = False): #par défaut, il n'y a pas de checksum
        if calcchecksum:
            prefix = "N" + str(lineno) + " " + command
            command = prefix + "*" + str(self._checksum(prefix))
        if self.printer:
            try:
                self.printer.write((command + "\n").encode('ascii')) #.write de serial écrit dans la liaison série
            except :
                print("erreur d'envoi")
                return


    def _checksum(self, command):
        	return reduce(lambda x, y: x ^ y, map(ord, command)) #ord renvoie le code unicode d'un caractère, map va appliquer la fonction ord à chaque élément (caractère) de command
		#reduce va ensuite calculer des puissances sur ces codes : (((premier)^deuxième)^troisième)^... et va renvoyer le résultat final

#----------------------------------------gestion des retours de l'imprimante (méthodes privées)--------------------------------------------------------------------
    
    
    def _listen(self):#cette fonction écoute sur le port série si l'imprimante parle
        self._listen_until_online() #ici on initialise la communication avec l'imprimante (test si elle répond) : cf la fonction juste dessous
        while self._listen_can_continue():
            line = self._readline()
            if line is None: #si il y a eu un problème
                break
            if line.startswith(tuple(self.greetings)) or line.startswith('ok'):
                print("l imprimante est ok, elle a renvoyé :"+line)
            if line.startswith('Error'):
                print("l imprimante a renvoyé une erreur :"+line)
            #else :
            #    print("l'imprimante a renvoyé :"+line)
        #ici on pourra gérer le fait que l'imprimante demande de renvoyer une commande
        print("on est sorti de la fonction _listen")
  

    def _listen_until_online(self): #permet de mettre self.online à True si la communication fonctionne et qu'on a reçu une première réponse de l'imprimante !
        compteur_tentatives = 0
        while not self.online and self._listen_can_continue(): #si on n'a pas reçu de réponse d'activation de l'imprimante et qu'on peut toujours écouter
            self._send("M105") #on envoie une commande de demande de rapport de température
            print("envoi de M105")
            if compteur_tentatives >= 4:
                print("on a tenté 4 fois d'envoyer une commande d'initialisation, mais on n'a jamais eu de réponse")
                return #on sort, ça ne sert à rien de continuer à envoyer des commandes d'initialisation
            while self._listen_can_continue():
                line = self._readline() #on récupère ce qu'on a lu dans le buffer. Peut valoir None si il n'y a rien dans le buffer ou None si un problème est survenu
                #line sera soit None (problème de lecture), soit une chaine de caractère non vide (l'imprimante a répondu), soit une chaine de caractère vide (rien dans le buffer, l'imprimante n'a pas encore répondu)
                if line is None: break  # exception levée dans _readline(), on essaye de réenvoyer un M105 (jusqu'à 4 fois)
                if line.startswith(tuple(self.greetings)) or line.startswith('ok') or "T:" in line: #si l'imprimante a répondu au M105 envoyé
                    self.online = True #on dit que l'imprimante a répondu et que la communication est établie
                    print("l imprimante a répondu à M105, communication établie. On peut envoyer du Gcode")
                    return
                elif line is not "":
                    print("apres M105, l imprimante n a pas dit que c etait ok mais a repondu :"+line)


    def _listen_can_continue(self):
        return (not self.stop_read_thread and self.printer and self.printer.is_open) #on retourne True si le thread de lecture est vivant et qu'on a une liaison série d'ouverte
        #en effet, on peut tuer le Thread de lecture en déconnectant l'imprimante, mais si on n'appelle pas cette fonction, le while de _listen continuera à jamais. Pareil si la liaison série est coupée.
    
    
    def _readline(self):
        try:
            line_bytes = self.printer.readline() #méthode de serial, qui permet de lire les octets du buffer série jusqu'à l'occurence d'un '\n'. Lève OSError si il n'y a rien à lire
            if line_bytes is None: #si jamais le readtimeout (défini lors de l'initialisation  de l'objet serial à 0.25s) est atteint sans avoir rien lu
                print("problème de lecture du buffer : imprimante déconnectée ?")
                return None #on retourne None qui dit qu'on n'a rien pu récupérer dans le buffer
            line = line_bytes.decode('utf-8') #on converti les octets récupérés en caractères
            return line #on retourne les caractères lus
        except OSError as e:
            if e.errno == errno.EAGAIN:  # c'est pas vraiment une erreur, c'est juste qu'il n'y a rien à lire dans le buffer
                return "" #on retourne une chaîne de caractère vide
            return None #au cas où
        except:
            print("problème de lecture du buffer : imprimante déconnectée ?")
            return None #si une exception autre qu'un buffer vide est levé

#----------------------------------------méthodes publiques--------------------------------------------------------------------

    def send(self, command): #méthode publique pour envoyer une commande en Gcode (n'importe laquelle, un homing G28 par exemple)
        if self.online:
            self.queue.put_nowait(command)
        else:
            print("pas connecté à l'imprimante")


    def sendxyz(self,x,y,z): #G0 X10 Y10 Z10 par exemple pour aller en (10,10,10). Le codage de l'UX obligera forcément à renvoyer un triplet d'Int
    #si la case x de l'UX n'est pas remplie, alors x="". x,y,z sont directement récupérés en str par l'ui
        x=" X"+x
        y=" Y"+y
        z=" Z"+z
        command="G0"+x+y+z
        if self.online:
            self.queue.put_nowait(command)
        else:
            print("pas connecté à l'imprimante")
