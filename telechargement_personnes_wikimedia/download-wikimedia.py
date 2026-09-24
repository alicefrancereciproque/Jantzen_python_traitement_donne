#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
download_personnes_images.py

Télécharge les images Wikimedia Commons décrites dans personnes.json.

Pour chaque personne (id_archi) :
- le champ "media" donne le nom de fichier (utilisé pour nommer les deux images) ;
- le champ "thumb" donne l'URL de la vignette, téléchargée telle quelle
  dans le dossier "thumb" ;
- l'URL de l'image en pleine résolution est reconstruite à partir du chemin
  de hash présent dans "thumb" (ex: ".../thumb/c/c6/Fichier.jpg/250px-Fichier.jpg")
  et téléchargée dans le dossier "media".
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

THUMB_DIR = Path("thumb")
MEDIA_DIR = Path("media")

MEDIA_URL_RE = re.compile(r"/commons/thumb/(?P<hash_path>.+/[^/]+)/[^/]+$")


def sanitize_filename(filename: str) -> str:
    """Nettoie un nom de fichier."""
    return re.sub(r'[<>:"/\\|?*\x00-\x1f]', "_", filename).strip()


def download_with_retry(
    url: str,
    session: requests.Session,
    max_retries: int = 3,
    initial_delay: float = 5.0,
    user_agent: str = "ReciproqueImageDownloader/1.0",
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


def build_media_url(thumb: str | None):
    """
    Reconstruit l'URL de l'image en pleine résolution à partir du chemin
    de hash contenu dans l'URL de la vignette (champ "thumb").
    """
    if not thumb:
        return None

    path = thumb.split("?", 1)[0]
    match = MEDIA_URL_RE.search(path)
    if not match:
        return None

    return f"https://upload.wikimedia.org/wikipedia/commons/{match.group('hash_path')}"


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

    filename = sanitize_filename(urllib.parse.unquote(media))

    results = []

    media_url = build_media_url(thumb)
    if media_url:
        ok, msg = download_file(
            media_url,
            MEDIA_DIR / filename,
            session,
            max_retries,
            user_agent,
        )
        results.append(("media", filename, ok, msg))

    if thumb:
        ok, msg = download_file(
            thumb,
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
