#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
download_personnes_images.py

Télécharge les images Wikimedia Commons décrites dans personnes.json.

Pour chaque personne :
- télécharge la miniature (champ "thumb") dans thumb_jpg/
- télécharge l'image originale (champ "media") dans media_jpg/

Les fichiers sont enregistrés avec le nom indiqué dans le champ "media"
(exemple : Corroyer-Edouard.png).

Exemple :
    python download_personnes_images.py --input personnes.json
"""

import argparse
import json
import random
import re
import sys
import time
import urllib.parse
from pathlib import Path

import requests

BASE_URL = "https://upload.wikimedia.org/wikipedia/commons"

THUMB_DIR = Path("thumb_jpg")
MEDIA_DIR = Path("media_jpg")


def sanitize_filename(filename: str) -> str:
    """Nettoie un nom de fichier."""
    return re.sub(r'[<>:"/\\|?*\x00-\x1f]', "_", filename).strip()


def download_with_retry(
    url: str,
    session: requests.Session,
    max_retries: int = 3,
    initial_delay: float = 2.0,
    user_agent: str = "ReciproqueImageDownloader/1.0"
):
    """Télécharge une URL avec retry."""

    for attempt in range(max_retries):

        try:
            r = session.get(
                url,
                timeout=30,
                headers={"User-Agent": user_agent},
            )
            r.raise_for_status()
            return r

        except requests.RequestException as e:

            status = getattr(e.response, "status_code", None)

            if status == 429 and attempt < max_retries - 1:
                delay = initial_delay * (2 ** attempt) + random.random()
                print(f"⚠️ 429 - nouvelle tentative dans {delay:.1f}s")
                time.sleep(delay)
                continue

            raise

    return None


def download_file(
    url: str,
    destination: Path,
    session: requests.Session,
    max_retries: int,
    user_agent: str,
):
    """Télécharge un fichier."""

    if destination.exists():
        return True, "déjà présent"

    try:
        r = download_with_retry(
            url,
            session,
            max_retries=max_retries,
            user_agent=user_agent,
        )
    except requests.RequestException as e:
        return False, str(e)

    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(r.content)

    return True, "téléchargé"


def build_media_url(media: str, thumb: str | None):
    """
    Construit l'URL de l'image originale à partir du champ thumb.

    thumb :
        c/c2/Charles_Garnier_by_Nadar_-_Leniaud_2003_p142.jpg/250px-...

    devient :

        https://upload.wikimedia.org/wikipedia/commons/c/c2/Charles_Garnier_by_Nadar_-_Leniaud_2003_p142.jpg
    """

    if not thumb:
        return None

    parts = thumb.split("/")

    if len(parts) < 3:
        return None

    hash1 = parts[0]
    hash2 = parts[1]
    real_filename = parts[2]

    return f"{BASE_URL}/{hash1}/{hash2}/{real_filename}"

def build_thumb_url(thumb: str | None):
    if not thumb:
        return None
    return f"{BASE_URL}/thumb/{thumb}"


def download_person(
    person,
    session,
    delay,
    max_retries,
    user_agent,
):
    media = person.get("media")
    thumb = person.get("thumb")

    if not media:
        return []
    #
    # Nom du fichier enregistré
    #
    filename = sanitize_filename(urllib.parse.unquote(media))

    results = []

    #
    # URL de téléchargement
    #
    media_url = build_media_url(media, thumb)

    if media_url:
        ok, msg = download_file(
            media_url,
            MEDIA_DIR / filename,
            session,
            max_retries,
            user_agent,
        )

        results.append(("media", filename, ok, msg))

    #
    # Miniature
    #
    thumb_url = build_thumb_url(thumb)

    if thumb_url:

        ok, msg = download_file(
            thumb_url,
            THUMB_DIR / filename,
            session,
            max_retries,
            user_agent,
        )

        results.append(("thumb", filename, ok, msg))

    if delay:
        time.sleep(delay)

    return results


def main():

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--input",
        default="personnes.json",
        help="Fichier JSON",
    )

    parser.add_argument(
        "--delay",
        type=float,
        default=0.5,
        help="Délai entre téléchargements",
    )

    parser.add_argument(
        "--max-retries",
        type=int,
        default=3,
    )

    parser.add_argument(
        "--user-agent",
        default="ReciproqueImageDownloader/1.0 (contact: wendy.gervais@reciproque.fr)",
    )

    args = parser.parse_args()

    input_path = Path(args.input)

    if not input_path.exists():
        print(f"❌ Fichier introuvable : {input_path}")
        sys.exit(1)

    with input_path.open("r", encoding="utf-8") as f:
        personnes = json.load(f)

    if not isinstance(personnes, list):
        print("❌ Le JSON doit contenir un tableau.")
        sys.exit(1)

    THUMB_DIR.mkdir(exist_ok=True)
    MEDIA_DIR.mkdir(exist_ok=True)

    session = requests.Session()

    ok = 0
    skipped = 0
    failed = 0

    print(f"{len(personnes)} personnes trouvées.\n")

    for p in personnes:

        ident = p.get("id_archi")

        results = download_person(
            p,
            session,
            args.delay,
            args.max_retries,
            args.user_agent,
        )

        if not results:
            print(f"⏭️ {ident} : pas d'image")
            continue

        for kind, filename, success, message in results:

            if success:

                if message == "déjà présent":
                    skipped += 1
                    print(f"⏭️ {kind:<6} {filename}")

                else:
                    ok += 1
                    print(f"✅ {kind:<6} {filename}")

            else:
                failed += 1
                print(f"❌ {kind:<6} {filename} : {message}")

    print("\n---------------------------------------")
    print(f"Téléchargés : {ok}")
    print(f"Déjà présents : {skipped}")
    print(f"Échecs : {failed}")
    print("---------------------------------------")


if __name__ == "__main__":
    main()