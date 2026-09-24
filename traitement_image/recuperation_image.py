import json
import shutil
from pathlib import Path


def filtrer_et_copier_photos(
    fichier_json: str,
    dossier_dropbox: str,
    dossier_destination: str = "photos_selectionnees",
):
    """Lit photos.json et copie uniquement la première occurrence de chaque image

    référencée depuis le dossier Dropbox vers le dossier de destination.
    """
    path_dropbox = Path(dossier_dropbox)
    path_dest = Path(dossier_destination)

    # 1. Créer le dossier de destination s'il n'existe pas
    path_dest.mkdir(parents=True, exist_ok=True)

    # 2. Charger le JSON des photos
    print("Chargement du fichier photos.json...")
    with open(fichier_json, "r", encoding="utf-8") as f:
        photos = json.load(f)

    # 3. Récupérer la liste des noms de fichiers uniques recherchés
    fichiers_utiles = {
        p.get("fichier") for p in photos if p.get("fichier") is not None
    }
    print(f"Nombre de photos uniques à conserver : {len(fichiers_utiles)}")

    # 4. Copier les fichiers
    copies_reussies = 0
    fichiers_manquants = []

    print("Copie des photos en cours...")
    for nom_fichier in fichiers_utiles:
        # rglob cherche à la racine ET dans tous les sous-dossiers.
        # next(..., None) récupère le PREMIER fichier correspondant.
        source = next(path_dropbox.rglob(nom_fichier), None)

        if source is None:
            fichiers_manquants.append(nom_fichier)
            continue

        destination = path_dest / Path(nom_fichier).name
        shutil.copy2(source, destination)  # copy2 conserve les métadonnées
        copies_reussies += 1

    print("\n--- RAPPORT ---")
    print(
        f"✅ Photos copiées avec succès : {copies_reussies}/{len(fichiers_utiles)}"
    )

    if fichiers_manquants:
        print(f" {len(fichiers_manquants)} photos introuvables dans Dropbox.")
        with open("../donnees_traitees/donnees_traitees_jeu_3/photos_manquantes.json", "w", encoding="utf-8") as f_out:
            json.dump(fichiers_manquants, f_out, indent=2)


if __name__ == "__main__":
    filtrer_et_copier_photos(
        fichier_json="../donnees_brut_client/donnees_brut_jeu_3/photos.json",
        dossier_dropbox="/Users/alicefrance/reciproque Dropbox/Alice Francé/JANTZEN/00_SOURCES_EMPO/LES_PHOTOS",
        dossier_destination="../donnees_traitees/donnees_traitees_jeu_3/photos_jpg",
    )