import os
from pathlib import Path
from PIL import Image, ImageOps
import pillow_heif
from concurrent.futures import ProcessPoolExecutor

# Active le support HEIF / AVIF
pillow_heif.register_heif_opener()

input_folder = Path("./photos_jpg")
output_folder = Path("./photos_output")
output_folder.mkdir(parents=True, exist_ok=True)

def process_single_image(img_path):
    try:
        filename = img_path.stem

        # Chemins des 4 fichiers cibles
        f_thumb_avif = output_folder / f"{filename}_thumb.avif"
        f_thumb_webp = output_folder / f"{filename}_thumb.webp"
        f_full_avif  = output_folder / f"{filename}_full.avif"
        f_full_webp  = output_folder / f"{filename}_full.webp"

        # SÉCURITÉ / REPRISE : Si les 4 fichiers existent déjà, on saute l'image !
        if f_thumb_avif.exists() and f_thumb_webp.exists() and f_full_avif.exists() and f_full_webp.exists():
            return "SKIPPED"

        with Image.open(img_path) as img:
            img = ImageOps.exif_transpose(img)

            # 1. Vignette (Thumb) - max 400px
            img_thumb = img.copy()
            img_thumb.thumbnail((400, 400))
            img_thumb.save(f_thumb_avif, format="AVIF", quality=65)
            img_thumb.save(f_thumb_webp, format="WEBP", quality=75)

            # 2. Plein écran (Full) - max 1920px
            img_full = img.copy()
            img_full.thumbnail((1920, 1920))
            img_full.save(f_full_avif, format="AVIF", quality=75)
            img_full.save(f_full_webp, format="WEBP", quality=80)

        return "CONVERTED"
    except Exception as e:
        return f"ERROR: {img_path.name} ({e})"

def main():
    extensions = ("*.jpg", "*.jpeg", "*.png", "*.JPG", "*.JPEG")
    image_files = []
    for ext in extensions:
        image_files.extend(input_folder.glob(ext))

    total = len(image_files)
    print(f"🚀 Début du traitement pour {total} images...")

    # Récupère tous les cœurs CPU du Mac (souvent 8, 10 ou 12 sur MacBook Pro)
    max_workers = os.cpu_count() or 4
    print(f"⚡ Mode turbo activé : {max_workers} cœurs CPU utilisés en parallèle !\n")

    completed = 0
    converted_count = 0
    skipped_count = 0

    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        for result in executor.map(process_single_image, image_files):
            completed += 1

            if result == "SKIPPED":
                skipped_count += 1
            elif result == "CONVERTED":
                converted_count += 1

            # Affiche un statut tous les 200 fichiers ou à la fin
            if completed % 200 == 0 or completed == total:
                pct = (completed / total) * 100
                print(f"Progression : {completed}/{total} ({pct:.1f}%) | Faits : {converted_count} | Déjà existants : {skipped_count}")

    print("\n✅ Conversion terminée avec succès !")

if __name__ == "__main__":
    main()