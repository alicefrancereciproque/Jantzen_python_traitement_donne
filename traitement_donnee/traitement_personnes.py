import json
import os
import re


def nettoyer_nom_fichier(chaine: str) -> str:
    """Nettoie une chaîne pour qu'elle puisse servir de nom de fichier valide."""
    # Remplace les espaces et caractères non alphanumériques par un tiret du bas
    chaine_propre = re.sub(r"[^\w\-_]", "_", chaine)
    # Évite les tirets du bas consécutifs
    return re.sub(r"_+" , "_", chaine_propre).strip("_")


def decouper_json_personnes(fichier_source: str, dossier_destination: str):
    # 1. Création du dossier de sortie s'il n'existe pas
    os.makedirs(dossier_destination, exist_ok=True)

    # 2. Lecture du fichier JSON d'origine
    with open(fichier_source, "r", encoding="utf-8") as f:
        personnes = json.load(f)

    # 3. Parcours de chaque entrée et sauvegarde individuelle
    for personne in personnes:
        id_archi = personne.get("id_archi", "inconnu")
        libelle = personne.get("libelle", "personne")
        nom_fichier = f"id_archi_{id_archi}.json"
        chemin_complet = os.path.join(dossier_destination, nom_fichier)

        # Écriture du JSON individuel
        with open(chemin_complet, "w", encoding="utf-8") as f_out:
            json.dump(personne, f_out, ensure_ascii=False, indent=2)

    print(f" Terminé ! {len(personnes)} fichiers créés dans '{dossier_destination}'.")


# --- Exécution ---
if __name__ == "__main__":
    decouper_json_personnes(
        fichier_source="personnes_brut.json",
        dossier_destination="personnes"
    )