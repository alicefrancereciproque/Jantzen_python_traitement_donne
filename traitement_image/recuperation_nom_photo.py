import json

# 1. Lecture du fichier photos.json
input_filename = '../donnees_brut_jeu_2/photos.json'
output_filename = '../donnees_traitee_jeu_2/noms_photos.json'

def recuperer_noms_photos(input_filename, output_filename):
    with open(input_filename, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # S'assurer que 'data' est une liste d'objets JSON
    if isinstance(data, dict):
        data = [data]  # Si c'est un seul objet au lieu d'une liste
        
    # 2. Extraction du nom de chaque photo (champ 'fichier')
    noms_photos = [item['fichier'] for item in data if 'fichier' in item]

    # 3. Écriture de la liste dans un nouveau fichier JSON
    with open(output_filename, 'w', encoding='utf-8') as f:
        json.dump(noms_photos, f, ensure_ascii=False, indent=2)

    print(f"Extraction réussie ! {len(noms_photos)} noms de photos ont été enregistrés dans '{output_filename}'.")
 

if __name__ == "__main__":
    recuperer_noms_photos(
        input_filename = '../donnees_brut_client/donnees_brut_jeu_2/photos.json',
        output_filename = '../donnees_traitees/donnees_traitees_jeu_2/noms_photos.json'
    )