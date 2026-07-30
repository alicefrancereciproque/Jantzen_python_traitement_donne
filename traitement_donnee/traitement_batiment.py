import json
from pathlib import Path


def convertir_donnees(
    fichier_batiments: str, fichier_photos: str, dossier_sortie: str = "batiments"
):
    """Lit les bâtiments et photos, associe les photos à chaque bâtiment,
    extrait les termes Jantzen uniques et sauvegarde un fichier JSON par
    bâtiment.
    """
    # 1. Créer le dossier de sortie s'il n'existe pas
    dossier_path = Path(dossier_sortie)
    dossier_path.mkdir(parents=True, exist_ok=True)

    # 2. Charger les fichiers source
    print("Chargement des fichiers JSON...")
    with open(fichier_batiments, "r", encoding="utf-8") as f:
        batiments = json.load(f)

    with open(fichier_photos, "r", encoding="utf-8") as f:
        photos = json.load(f)

    # 3. Indexer les photos :
    # - Par batimentID pour regrouper les photos
    # - Par id_photo pour retrouver le nom de fichier via image_ref
    photos_par_batiment = {}
    fichier_par_id_photo = {}

    for photo in photos:
        # Nettoyage du nom de fichier (ex: "photo_01.jpg" -> "image_photo_01")
        nom_fichier_clean = f"{photo.get('fichier', '').removesuffix('.jpg')}"
        
        # On garde en mémoire quel nom de fichier correspond à quel ID de photo
        id_photo = photo.get("id") or photo.get("id_photo")  # Adapte le nom de la clé selon ton JSON photos_brut
        if id_photo is not None:
            fichier_par_id_photo[id_photo] = nom_fichier_clean

        bat_id = photo.get("batimentID")
        if bat_id is None:
            continue

        index_jantzen = photo.get("IndexJantzen") or []

        # Format attendu dans le JSON final pour la photo
        photo_formatee = {
            "id_pic": nom_fichier_clean,
            "IndexJantzen": index_jantzen,
            "dateCapture": photo.get("dateCapture"),
        }

        if bat_id not in photos_par_batiment:
            photos_par_batiment[bat_id] = []

        photos_par_batiment[bat_id].append(photo_formatee)

    # 4. Traiter chaque bâtiment et générer son JSON
    print("Génération des fichiers bâtiments...")
    count = 0

    for bat in batiments:
        id_bat = bat.get("id_bat")

        # Récupérer les photos associées à ce bâtiment
        liste_photos = photos_par_batiment.get(id_bat, [])

        # Extraire tous les termes Jantzen uniques des photos de ce bâtiment
        termes_set = set()
        for p in liste_photos:
            termes_set.update(p.get("IndexJantzen", []))

        # Récupérer l'ID de la photo de référence et le remplacer par le nom de fichier
        id_image_ref = bat.get("image_ref")
        image_ref_fichier = fichier_par_id_photo.get(id_image_ref, id_image_ref)

        # Créer une copie du dictionnaire original pour ajouter les nouveaux champs
        bat_enrichi = dict(bat)
        bat_enrichi["image_ref"] = image_ref_fichier
        bat_enrichi["terme_jantzen_bat"] = list(termes_set)
        bat_enrichi["photos"] = liste_photos

        # 5. Écrire le fichier JSON individuel
        nom_fichier = dossier_path / f"id_bat_{id_bat}.json"
        with open(nom_fichier, "w", encoding="utf-8") as f_out:
            json.dump(bat_enrichi, f_out, ensure_ascii=False, indent=2)

        count += 1

    print(
        f"✅ Terminé ! {count} fichiers générés dans le dossier '{dossier_sortie}'."
    )


# Exemple d'appel :
if __name__ == "__main__":
    convertir_donnees(
        fichier_batiments="batiments_brut.json",
        fichier_photos="photos_brut.json",
        dossier_sortie="batiments",
    )