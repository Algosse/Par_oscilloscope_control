Ce fichier contient les codes relatifs à un logiciel de contrôle d'un banc d'essai pour le scan électromagnétique d'une carte électronique pour la mise en place d'attaque par canal auxiliaire.
***********************************************************************
Son développement a été commencé dans le laboratoire INL à l'Ecole Centrale de Lyon par C.Marchand et continué par deux PAr (122 et 123) durant l'année scolaire 2020/2021.
***********************************************************************
A la reprise du code en septembre 2020 par les deux PAr, l'objectif était de reconnaitre le circuit à attaquer grâce à une caméra placée sur une imprimante 3D et de réaliser automatiquement le scan électromagnétique du circuit repéré. Ces nouvelles fonctions devaient être placées dans un nouvle onglet du logiciel
***********************************************************************
A partir du dossier initial, les fichiers suivants ont été ajoutés/modifiés :

PAr122
- rajout du fichier calibration.dat pour stocker des coordoonnées utiles à la reconnaissance de circuit
- modification de main.py pour rajouter directement les fonctions de reconnaissance de circuit et de gestion de la caméra, ainsi que pour lier l'ui et ces fonctions rajoutées
- modification de l'ui (via Qt Designer, qui travaille sur le fichier Oscilloscope_control.ui, et qui est transformé en Oscilloscope_control.py)

PAr123
- rajout d'une bibliothèque, communication_serie.py qui contient les classes et fonctions de gestion de la communication série avec l'imprimante 3D
- modification de l'ui en conséquence (via Qt Designer, qui travaille sur le fichier Oscilloscope_control.ui, et qui est transformé en Oscilloscope_control.py)
- modification du main.py pour lier l'ui et les classes/fonctions écrites dans communication_serie.py
***********************************************************************
A la date de rendu l'onglet rajouté sur le logiciel est capable de faire les actions suivantes :
- connecter le logiciel à l'imprimante et initialiser la communication
- déplacer la tête de l'imprimante via des coordonnées xyz relatives précisées
- envoyer des commandes générales en Gcode
- fournir une image vidéo du plateau de l'imprimante sur lequel doit être placé le circuit
- réaliser une calibration pour prendre en compte l'homographie spatiale due à la caméra
- placer manuellement sur l'image fournie par la caméra les sommets du composant à scanner
- lancer une première approche automatique de la tête au dessus d'un sommet du composant
- réglage précis manuel (nécessaire en altitude z pour être au plus proche du composant) via le déplacement xyz
- réglage d'un pas de parcours du composant
- lancement de l'attaque depuis la position courante de la tête (au moins en z), à l'intérieur du rectangle fixé précédemment, et selon le pas précisé précédemment
***********************************************************************
Etapes pour lancer un scan :
0) via une console ouverte dans ce dossier, lancer le main.py avec python. La fenêtre du logiciel apparaît
1) changer la caméra pour switcher sur celle de l'imprimante
2) appuyer sur le bouton de connexion à l'imprimante et attendre la fin  du homming
3) cliquer sur les 4 coins du plateau de l'imprimante sur l'image fournie par la caméra
4) appuyer sur calibrate : la vue de la caméra doit changer pour s'adapter à l'homographie
5) placer manuellement chacun des points du circuit intégré à scaner : on appuie sur "place" et on clique à l'écran sur le point correspondant (top left, top right, bottom left)
6) appuyer sur le bouton approach : la tête doit se placer au dessus du point top left du circuit
7) régler la hauteur z manuellement grâce à la box printer xyz : il faut descendre petit à petit la tête de la sonde en fixant un pas z négatif (plus petit à mesure qu'on a pproche du circuit pour ne pas détruire les moteurs en cas de déplacement interdit)
8) on règle le step (le pas de parcours du composant)
9) on appuie sur start attack pour lancer le scan du circuit