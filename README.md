# Projet Jantzen_python_traitement_donne

## Description
Ce projet s'inscrit dans le cadre du projet Jantzen-Torne-H pour le musée d'Orsay.

Le but de ce projet est de traiter les JSON envoyés par le client, contenant l'ensemble des données utilisées dans l'application web que nous avons développée.
Les JSON envoyés par le client, dits « JSON bruts », sont ici « découpés » en plusieurs JSON utilisables, les « JSON traités » pour l'application web. Ce traitement est réalisé en langage Python.

Le projet contient aussi des scripts annexes pour :
- télécharger les portraits des personnes depuis Wikimedia Commons ;
- générer un index allégé du thésaurus pour l'interface.

### Chaîne de traitement

```
.
├── donnees_brut_client/          JSON bruts envoyés par le client (un dossier par livraison)
├── donnees_traitees/             JSON produits par les scripts (un dossier par livraison)
├── traitement_donnee/            Scripts de découpage / transformation des JSON
├── traitement_image/             Scripts liés aux photos des bâtiments
├── telechargement_personnes_wikimedia/   Téléchargement des portraits des personnes
└── tools_thesaurus/              Génération de l'index du thésaurus pour l'interface
```


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

| Dossier | Livraison | batiments.json | personnes.json | photos.json | Remarques |
|-----------|-----------|-----------|-----------|-----------|-----------|
| donnees_brut_jeu_1 | 22/07/2026 | 1 574 | 732 (avec doublons et duos) | 9 744 | Pas de champ `tri_alphab` |
| donnees_brut_jeu_2 | 24/08/2026 | 1 661 | 805 (sans doublon ni duo, uniquement des architectes) | 9 908 | |
| donnees_brut_jeu_3 | 24/09/2026 | 3 065 | 955 | 13 344 | |
| donnees_brut_final | 19/10/2026 | 3 064 | — | 13 344 | Pas de `personnes.json` : les personnes du jeu 3 restent la référence |

### donnees_traitees

Chaque dossier contient les fichiers produits à partir du dossier brut correspondant (ex. `donnees_traitees_jeu_3` ← `donnees_brut_jeu_3`).

| Fichier / dossier | Contenu | Généré par | Utilisé dans l'app ? |
|-----------|-----------|-----------|-----------|
| batiments/ | Un JSON par bâtiment, nommé `id_bat_<id>.json`. Reprend les champs du bâtiment brut, avec `image_ref` remplacé par le nom de fichier de la photo, et ajoute `terme_jantzen_bat`, `terme_torneh_bat` et la liste `photos` (`id_pic`, `IndexJantzen`, `IndexTorneh`, `dateCapture`) | traitement_batiment.py | OUI |
| personnes/ | Un JSON par personne, nommé `id_archi_<id>.json` | traitement_personnes.py | OUI |
| photos_jpg/ | Photos JPG des bâtiments (non versionnées, cf. `.gitignore`) | recuperation_image.py | OUI |
| map_poi.geojson | `FeatureCollection` GeoJSON (format Leaflet) : un point par bâtiment avec les propriétés utiles à l'affichage et aux filtres de la carte | traitement_poi.py | OUI |
| personnes_filtre.json | Liste allégée des personnes (`id_archi`, `libelle`, `nom`) pour le filtre des architectes et artistes | traitement_personnes_filtre.py | OUI |
| periode_filtre.json | JSON permettant d'afficher le filtre par période (jeux 1 et 2 uniquement) | Aucun script dans ce dépôt | OUI |
| photos_manquantes.json | Noms des photos citées dans `photos.json` mais introuvables dans la Dropbox | recuperation_image.py | NON |
| noms_photos.json | Liste des noms des photos, pour chercher rapidement une photo lors des tests (jeu 2 uniquement) | recuperation_nom_photo.py | NON |
| modifications_photos.json | Correspondance entre les noms de photos d'origine contenant un « ç » et leur nom corrigé (jeu 3 uniquement, 21 photos) | Aucun script dans ce dépôt | NON |

Contenu par jeu :

| Dossier | batiments/ | personnes/ | map_poi.geojson | Autres fichiers |
|-----------|-----------|-----------|-----------|-----------|
| donnees_traitees_jeu_1 | 1 574 (+ 1 574 anciens fichiers `id_batt_<id>.json` en double) | 704 | 1 574 points | periode_filtre, personnes_filtre, photos_manquantes |
| donnees_traitees_jeu_2 | — | 805 | 1 661 points | periode_filtre, personnes_filtre, photos_manquantes, noms_photos |
| donnees_traitees_jeu_3 | 3 065 | 955 | 3 065 points | personnes_filtre, photos_manquantes, modifications_photos, batiments_sans_c_cedille |
| donnees_traitees_final | 3 064 | — | 3 064 points | |


## Scripts

### traitement_donnee

| Fichier Python | Fichier(s) d'entrée (brut) | Sortie (traité) | Remarques |
|-----------|-----------|----------|----------|
| traitement_batiment.py | batiments.json, photos.json, thesaurus_torneh.json | batiments/ | Associe les photos à chaque bâtiment, traduit les `termesIndexIds` en termes Torneh et dédoublonne les termes Jantzen et Torneh au niveau du bâtiment. Affiche un avertissement pour les IDs absents du thésaurus. |
| traitement_poi.py | batiments.json, photos.json, thesaurus_torneh.json | map_poi.geojson | Ignore les bâtiments sans coordonnées valides. Les coordonnées sont au format GeoJSON `[longitude, latitude]`. |
| traitement_personnes.py | personnes.json | personnes/ | Un fichier par `id_archi`. |
| traitement_personnes_filtre.py | personnes.json | personnes_filtre.json | ⚠️ La boucle de dédoublonnage par `id_archi` est écrasée par la liste construite juste après : les doublons éventuels ne sont donc pas supprimés. |

### traitement_image

| Fichier Python | Fichier d'entrée (brut) | Sortie (traité) | Remarques |
|-----------|-----------|----------|----------|
| recuperation_image.py | photos.json + dossier Dropbox des photos | photos_jpg/, photos_manquantes.json | Copie uniquement les photos citées dans `photos.json` (recherche récursive dans la Dropbox), pour ne pas avoir un dossier de 14 000 photos alors qu'on ne les utilise pas toutes. Le chemin Dropbox est propre à chaque poste, et le chemin de `photos_manquantes.json` est écrit en dur dans la fonction (jeu 3) : à adapter. |
| recuperation_nom_photo.py | photos.json | noms_photos.json | Récupère la liste des noms des photos, pour chercher rapidement parmi eux (tests, bugs). |
| convertisseur.py | photos_jpg/ | photos_output/ | Non abouti. Convertit les JPG en WebP et AVIF (vignette 400 px et plein écran 1920 px), mais le temps d'exécution n'est pas satisfaisant au vu du nombre de photos. Nécessite `Pillow` et `pillow-heif`. |

### telechargement_personnes_wikimedia

`download-wikimedia.py` télécharge, pour chaque personne de `personnes.json` qui a un champ `media` :
- la vignette (URL du champ `thumb`) dans le dossier `thumb/` ;
- l'image en pleine résolution (URL reconstruite à partir de `thumb`) dans le dossier `media/`.

Les fichiers déjà présents sont ignorés, et les erreurs 429 (trop de requêtes) sont relancées avec un délai croissant. Les dossiers `thumb/` et `media/` ne sont pas versionnés.

```bash
cd telechargement_personnes_wikimedia
python download-wikimedia.py --input personnes.json --delay 0.5 --max-retries 3
```

Options : `--input` (défaut `personnes.json`), `--delay` (délai entre deux téléchargements, défaut 0,5 s), `--max-retries` (défaut 3), `--user-agent`.

### tools_thesaurus

`build_indexes.py` génère `thesaurus_index.json`, une version allégée de `thesaurus_jantzen.json` (sans les définitions) utilisée pour construire l'arborescence des filtres de l'interface. Chaque terme y est réduit à `{t: terme, c: cluster, u: URL, s: source}`.

```bash
python tools_thesaurus/build_indexes.py
```

La fonction `build_batiments_index()` (index `id_bat -> {années, nombre de photos}`) est présente mais désactivée : elle attend un dossier `tools_thesaurus/batiments/` qui n'existe pas dans le dépôt.

## Installation

### Prérequis
* **Python 3.10+** (les scripts utilisent `str.removesuffix` et la syntaxe de type `str | None`)

### Environnement virtuel

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install requests              # pour download-wikimedia.py
pip install Pillow pillow-heif    # uniquement pour convertisseur.py
```

Les scripts de `traitement_donnee/` n'utilisent que la bibliothèque standard.

## Utilisation

Les chemins d'entrée et de sortie sont relatifs et écrits en bas de chaque script (bloc `if __name__ == "__main__":`). Il faut donc lancer les scripts **depuis leur propre dossier**.

1. Placez les nouveaux JSON du client dans un nouveau dossier `donnees_brut_client/donnees_brut_<jeu>/`.
2. Dans chaque script, mettez à jour les chemins d'entrée et de sortie en bas du fichier pour pointer vers ce jeu.
3. Lancez les scripts :

```bash
cd traitement_donnee
python traitement_batiment.py
python traitement_poi.py
python traitement_personnes.py
python traitement_personnes_filtre.py

cd ../traitement_image
python recuperation_image.py
```

4. Copiez le contenu de `donnees_traitees/donnees_traitees_<jeu>/` dans l'application web.

> Les scripts écrasent les fichiers existants mais ne suppriment pas les anciens : si des bâtiments ou des personnes ont disparu d'un jeu à l'autre, videz le dossier de sortie avant de relancer le traitement.
