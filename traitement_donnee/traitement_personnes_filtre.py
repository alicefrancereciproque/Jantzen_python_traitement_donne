import json
import os


def filtrer_json_personnes(fichier_source: str, fichier_sortie: str):
    """
    Lit un fichier JSON d'origine et génère un nouveau JSON contenant
    uniquement les champs 'id_archi' et 'libelle' pour chaque entrée.
    """
    # 1. Lecture du fichier JSON d'origine
    with open(fichier_source, "r", encoding="utf-8") as f:
        personnes = json.load(f)

    personnes_filtrees = []
    ids_vus = set()

    for personne in personnes:
        id_archi = personne.get("id_archi")

        if id_archi not in ids_vus:
            ids_vus.add(id_archi)
            personnes_filtrees.append({
                "id_archi": id_archi,
                "libelle": personne.get("libelle"),
            })

    # 2. Filtrage : on ne conserve que 'id_archi' et 'libelle'
    personnes_filtrees = [
        {
            "id_archi": personne.get("id_archi"),
            "libelle": personne.get("libelle"),
        }
        for personne in personnes
    ]

    # 3. Création du dossier de destination si nécessaire
    dossier_sortie = os.path.dirname(fichier_sortie)
    if dossier_sortie:
        os.makedirs(dossier_sortie, exist_ok=True)

    # 4. Écriture du fichier JSON filtré
    with open(fichier_sortie, "w", encoding="utf-8") as f_out:
        json.dump(personnes_filtrees, f_out, ensure_ascii=False, indent=2)

    print(f"Terminé ! {len(personnes_filtrees)} entrées écrites dans '{fichier_sortie}'.")


# --- Exécution ---
if __name__ == "__main__":
    filtrer_json_personnes(
        fichier_source="personnes_brut.json",
        fichier_sortie="personnes_filtre.json",
    )