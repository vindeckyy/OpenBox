"""Safe, cached extraction for compressed game files."""

import hashlib
import shutil
import subprocess
import zipfile
from pathlib import Path


def extraction_dir(archive, cache_root):
    stat = archive.stat()
    digest = hashlib.sha256(f"{archive.resolve()}:{stat.st_size}:{stat.st_mtime_ns}".encode()).hexdigest()[:20]
    return cache_root / digest


def safe_zip_extract(archive, destination):
    root = destination.resolve()
    with zipfile.ZipFile(archive) as package:
        for info in package.infolist():
            target = (destination / info.filename).resolve()
            if root != target and root not in target.parents:
                raise ValueError(f"Unsafe archive path: {info.filename}")
        package.extractall(destination)


def choose_game_file(destination, member=""):
    if member:
        selected = (destination / member).resolve()
        if destination.resolve() not in selected.parents or not selected.is_file():
            raise FileNotFoundError(f"Archive member not found: {member}")
        return selected
    ignored = {".txt", ".nfo", ".diz", ".jpg", ".jpeg", ".png", ".gif", ".pdf"}
    files = [path for path in destination.rglob("*") if path.is_file() and path.name != ".complete" and path.suffix.lower() not in ignored]
    if not files:
        raise FileNotFoundError("No launchable file was found in the archive.")
    return max(files, key=lambda path: path.stat().st_size)


def extract_game(archive_path, cache_root, member=""):
    archive = Path(archive_path)
    destination = extraction_dir(archive, Path(cache_root))
    complete = destination / ".complete"
    if not complete.is_file():
        destination.mkdir(parents=True, exist_ok=True)
        if archive.suffix.lower() == ".zip":
            safe_zip_extract(archive, destination)
        else:
            extractor = shutil.which("7z") or shutil.which("7zz")
            if not extractor:
                raise FileNotFoundError("7z or 7zz is required to extract this archive.")
            subprocess.run([extractor, "x", "-y", f"-o{destination}", str(archive)], check=True, capture_output=True)
        complete.touch()
    return choose_game_file(destination, member)
