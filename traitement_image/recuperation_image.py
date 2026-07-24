import json
import shutil
from pathlib import Path


def filtrer_et_copier_photos(
    fichier_json: str,
    dossier_dropbox: str,
    dossier_destination: str = "photos_selectionnees",
):
    """Lit photos.json et copie uniquement les images référencées depuis le dossier

    Dropbox vers le dossier de destination.
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
        source = path_dropbox / nom_fichier

        # Si tes photos sont dans des sous-dossiers dans Dropbox, on peut chercher recursively :
        if not source.exists():
            # Chercher dans les sous-dossiers
            trouves = list(path_dropbox.rglob(nom_fichier))
            if trouves:
                source = trouves[0]
            else:
                fichiers_manquants.append(nom_fichier)
                continue

        destination = path_dest / nom_fichier
        shutil.copy2(source, destination)  # copy2 conserve les métadonnées
        copies_reussies += 1

    print("\n--- RAPPORT ---")
    print(
        f"✅ Photos copiées avec succès : {copies_reussies}/{len(fichiers_utiles)}"
    )

    if fichiers_manquants:
        print(f"⚠️ {len(fichiers_manquants)} photos introuvables dans Dropbox.")
        # Optionnel : enregistrer la liste des manquants
        with open("photos_manquantes.json", "w", encoding="utf-8") as f_out:
            json.dump(fichiers_manquants, f_out, indent=2)


if __name__ == "__main__":
    # 💡 REMPLACE CES CHEMINS PAR LES TIENS :
    # Si Dropbox est synchronisé sur ton PC, met le chemin local (ex: "C:/Users/TonNom/Dropbox/Photos")
    filtrer_et_copier_photos(
        fichier_json="photos_brut.json",
        dossier_dropbox="/Users/alicefrance/reciproque Dropbox/Alice Francé/JANTZEN/00_SOURCES_EMPO/LES_PHOTOS",  # Remplace par ton vrai chemin
        dossier_destination="./photos_selectionnees",
    )