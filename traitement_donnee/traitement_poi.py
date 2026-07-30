import json


def generer_geojson_leaflet(
    fichier_batiments: str,
    fichier_photos: str,
    fichier_sortie: str = "map_poi.geojson",
):
    """Génère un fichier GeoJSON strictement conforme aux spécifications Leaflet

    à partir des bâtiments et photos bruts.
    """
    print("Chargement des données JSON...")
    with open(fichier_batiments, "r", encoding="utf-8") as f:
        batiments = json.load(f)

    with open(fichier_photos, "r", encoding="utf-8") as f:
        photos = json.load(f)

    # 1. Regrouper les termes Jantzen uniques par ID de bâtiment
    termes_par_batiment = {}
    for photo in photos:
        bat_id = photo.get("batimentID")
        if bat_id is None:
            continue

        index_jantzen = photo.get("IndexJantzen") or []

        if bat_id not in termes_par_batiment:
            termes_par_batiment[bat_id] = set()

        termes_par_batiment[bat_id].update(index_jantzen)

    # 2. Construire les "Features" GeoJSON au standard Leaflet
    features = []

    for bat in batiments:
        id_bat = bat.get("id_bat")
        coords = bat.get("coordonnees")

        # Sécurité : ignorer les bâtiments sans coordonnées valides
        if not coords or "longitude" not in coords or "latitude" not in coords:
            continue

        try:
            lng = float(coords["longitude"])
            lat = float(coords["latitude"])
        except (ValueError, TypeError):
            continue

        # Récupération et tri des termes Jantzen uniques
        termes_jantzen = sorted(list(termes_par_batiment.get(id_bat, set())))

        # ⚠️ STRUCTURE STRATEGIQUE : Standard GeoJSON / Leaflet
        feature = {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                # Clé "coordinates" (et non "coordonnees") : Longitude puis Latitude [lng, lat]
                "coordinates": [lng, lat],
            },
            "properties": {
                "id_bat": id_bat,
                "libelle": bat.get("libelle") or "",
                "ensemble": bat.get("ensemble") or "",
                "adresse": {
                    "numero": (bat.get("adresse") or {}).get("numero"),
                    "voie": (bat.get("adresse") or {}).get("voie")
                },
                "arrondissement": (
                    int(bat.get("arrondissement"))
                    if bat.get("arrondissement")
                    else None
                ),
                "dateConstruction": bat.get("dateConstruction") or "",
                "periode": bat.get("periode") or "",
                "personneID": (bat.get("personnes") or [{}])[0].get("personneID") or 1,
                "role": (bat.get("personnes") or [{}])[0].get("role") or "",
                "image_ref": bat.get("image_ref"),
                "terme_jantzen_bat": termes_jantzen,
            },
        }

        features.append(feature)

    # 3. Assembler la FeatureCollection globale
    geojson = {"type": "FeatureCollection", "features": features}

    # 4. Sauvegarder dans le fichier GeoJSON final
    with open(fichier_sortie, "w", encoding="utf-8") as f_out:
        json.dump(geojson, f_out, ensure_ascii=False, indent=2)

    print(
        f"✅ GeoJSON compatible Leaflet créé avec succès !"
        f"\n📍 {len(features)} points enregistrés dans '{fichier_sortie}'."
    )


# Exécution :
if __name__ == "__main__":
    generer_geojson_leaflet(
        fichier_batiments="batiments_brut.json",
        fichier_photos="photos_brut.json",
        fichier_sortie="map_poi.geojson",  # Destination dans ton projet web
    )