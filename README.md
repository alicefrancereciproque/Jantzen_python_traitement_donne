
# Projet Jantzen_python_traitement_donne

## Description
Ce projet s'inscrit dans le cadre du projet Jantzen-Torn-h pour le musée d'Orsay.

Le but de ce projet est de traiter les JSON envoyés par le client, contenant l'ensemble des données utilisées dans l'application web que nous avons développée.
Les JSON envoyés par le client, dits « JSON bruts », sont ici « découpés » en plusieurs JSON utilisables, les « JSON traités » pour l'application web. Ce traitement est réalisé en langage Python.

### Arborescence 

#### donnees_brut_client

**donnees_brut_jeu_1**
Ensemble des fichiers JSON correspondant au premier jeu de données envoyé par le client (le 22/07/2026).

| Fichier | Contenu | Utilisé dans l'app ? |
|-----------|-----------|-----------|
| batiments.json | 1 575 entités | NON |
| personnes.json | 733 personnes (avec des doublons et des duos) | NON |
| thesaurus_torneh.json | Indexations de Jantzen | OUI |
| photos.json | 9 744 photos (seulement celles liées aux bâtiments). Chaque photo a son indexation du thésaurus associée et le bâtiment auquel elle se réfère | NON |

**donnees_brut_jeu_2**
Ensemble des fichiers JSON correspondant au deuxième jeu de données envoyé par le client (le 24/08/2026).

| Fichier | Contenu | Utilisé dans l'app ? |
|-----------|-----------|-----------|
| batiments.json | 1 660 entités | NON |
| personnes.json | 805 personnes (sans doublon, sans duo mais uniquement avec des rôles d'architectes) | NON |
| thesaurus_torneh.json | ISO au premier | OUI |
| photos.json | Ensemble des photos liées aux bâtiments | NON |

#### donnees_traitees

**donnees_traitees_jeu_1**
Ensemble des JSON créés à l'aide des scripts Python. Ils se basent sur les JSON de *donnees_brut_jeu_1*.

| Fichier | Contenu | Utilisé dans l'app ? |
|-----------|-----------|-----------|
| batiments | Dossier composé d'un JSON par bâtiment. Les JSON sont nommés par l'identifiant (ID) du bâtiment correspondant | OUI |
| personnes | Dossier composé d'un JSON par personne. Les JSON sont nommés par l'identifiant (ID) de la personne correspondante | OUI |
| photos_jpg | Dossier contenant l'ensemble des photos au format JPG correspondant aux bâtiments | OUI |
| map_poi.geojson | Contient les informations sur les POI pour les afficher sur la carte et les filtrer rapidement | OUI |
| periode_filtre.json | JSON permettant d'afficher le filtre par période | OUI |
| personnes_filtre.json | JSON permettant d'afficher le filtre des architectes et artistes | OUI |
| photos_manquantes.json | JSON permettant d'identifier les photos manquantes lors de la création du fichier photo | NON |

**donnees_traitees_jeu_2**
Ensemble des JSON créés à l'aide des scripts Python. Ils se basent sur les JSON de *donnees_brut_jeu_2*.

| Fichier | Contenu | Utilisé dans l'app ? |
|-----------|-----------|-----------|
| batiments | Dossier composé d'un JSON par bâtiment. Les JSON sont nommés par l'identifiant (ID) du bâtiment correspondant | OUI |
| personnes | Dossier composé d'un JSON par personne. Les JSON sont nommés par l'identifiant (ID) de la personne correspondante | OUI |
| photos_jpg | Dossier contenant l'ensemble des photos au format JPG correspondant aux bâtiments | OUI |
| map_poi.geojson | Contient les informations sur les POI pour les afficher sur la carte et les filtrer rapidement | OUI |
| periode_filtre.json | JSON permettant d'afficher le filtre par période | OUI |
| personnes_filtre.json | JSON permettant d'afficher le filtre des architectes et artistes | OUI |
| noms_photos.json | Ensemble des noms des photos. Ce JSON permet de simplifier les recherches dans le fichier des photos pour faire des tests | NON |
| photos_manquantes.json | JSON permettant d'identifier les photos manquantes lors de la création du fichier photo | NON |

#### telechargement_personnes_wikimedia
download-wikimedia.py

#### traitement_donnee
| Fichier Python | Fichier d'entrée (brut) | Fichier de sortie (traité) | Remarques |
|-----------|-----------|----------|----------|
| traitement_batiment.py | batiments.json, photos.json | batiments | |
| traitement_personnes_filtre.py | personnes.json | personnes_filtre.json | |
| traitement_personnes.py | personnes.json | personnes | |
| traitement_poi.py | batiments.json, photos.json | map_poi.geojson | |

#### traitement_image
| Fichier Python | Fichier d'entrée (brut) | Fichier de sortie (traité) | Remarques |
|-----------|-----------|----------|----------|
| convertisseur.py | photos.json |-- | Ce code n'est pas abouti. Le but était de convertir les fichiers JPG en WebP et AVIF, mais le temps d'exécution n'est pas satisfaisant au vu du nombre de photos. |
| recuperation_image.py | photos.json | photo_jpg | Crée un fichier contenant l'ensemble des photos JPG qui sont citées dans le fichier photos.json. Cela permet de ne pas avoir un dossier de 14 000 photos alors qu'on ne les utilise pas toutes. |
| recuperation_nom_photo.py | photos.json | noms_photos.json | Permet de récupérer la liste des noms des photos qui sont dans le fichier photos.json. Ce fichier permet de chercher rapidement parmi les noms de photos pour tester des bugs notamment. |

## Utilisation

Pour exécuter le code :

1. Depuis le terminal, déplacez-vous dans le dossier contenant le code: `cd path/to/folder` et `cd ..` pour revenir en arrière.
2. Dans le fichier de code, vérifiez que les chemins des fichiers d'entrée et de sortie situés à la fin du script sont corrects.
3. Dans le terminal, exécutez la commande suivante : `python nom_du_fichier.py`

## Installation

### Prérequis
* **Python 3.8+**
