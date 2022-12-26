# Git repository 11-decembre-p10
## PROJET 10


# 1.Initialisation des environnements LUIS
# 1.1 preparation des données

$ python prep_luis_data.py 
Initialisation de l'extraction des données : OK.
!########################################################################################################################################### 
!###
!### -->  Initialisation des données :
!### -->  Fichier d'entrainement : ./model_data/training_data.csv
!### -->  Fichier de test : ./model_data/test_data.csv
!###
!###########################################################################################################################################
(100, 12)
(100, 12)
Initialisation completed successfully   [0.26 min.] : ./model_data/training_data.csv
$ lr model_data/

-rw-rw-r-- 1 grunix grunix     26 Dec 26 23:20 msaFileInitialisationLock.txt

-rw-rw-r-- 1 grunix grunix 200705 Dec 26 23:20 training_data.csv

-rw-rw-r-- 1 grunix grunix  17194 Dec 26 23:20 test_data.csv

-rw-rw-r-- 1 grunix grunix  37477 Dec 26 23:20 utterances_for_test.json
$

# 1.2 Creation des applications LUIS

Creer la ressource LuisAuthoring 

Renseigner le fichier application.config

$ cat application.conf 
authoring_endpoint = 'XX'
authoring_key_1 = 'XX'
authoring_key_2 = 'XX'
$

Lancer le script manage_luis_apps.py
$ python manage_luis_apps.py

