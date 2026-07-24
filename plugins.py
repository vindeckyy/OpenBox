"""Local OpenBox plugin packages and hooks."""

import json
import re
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime
from pathlib import Path

from archives import safe_zip_extract


HOOKS = {"before_launch", "after_session", "library"}
PLUGIN_ID = re.compile(r"^[a-z0-9][a-z0-9._-]{1,63}$")
RUNNER = Path(__file__).with_name("plugin_runner.py")


def state_file(directory):
    return Path(directory) / "plugins-state.json"


def load_plugin_state(directory):
    try:
        data = json.loads(state_file(directory).read_text())
        return data if isinstance(data, dict) else {}
    except (OSError, json.JSONDecodeError):
        return {}


def save_plugin_state(directory, state):
    path = state_file(directory)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(".tmp")
    temporary.write_text(json.dumps(state, indent=2))
    temporary.replace(path)


def read_manifest(path):
    try:
        manifest = json.loads((path / "plugin.json").read_text())
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError("Plugin package needs a valid plugin.json.") from error
    plugin_id = str(manifest.get("id", ""))
    entry = str(manifest.get("entry", "plugin.py"))
    hooks = manifest.get("hooks", [])
    if not PLUGIN_ID.fullmatch(plugin_id) or not manifest.get("name") or not manifest.get("version"):
        raise ValueError("Plugin id, name, and version are required.")
    if not isinstance(hooks, list) or not set(hooks) <= HOOKS:
        raise ValueError("Plugin declares an unsupported hook.")
    entry_path = (path / entry).resolve()
    if path.resolve() not in entry_path.parents or not entry_path.is_file() or entry_path.suffix != ".py":
        raise ValueError("Plugin entry must be a Python file inside the package.")
    return {**manifest, "id":plugin_id, "entry":entry, "hooks":hooks}


def list_plugins(directory):
    root = Path(directory)
    disabled = set(load_plugin_state(root).get("disabled", []))
    plugins = []
    if root.is_dir():
        for path in sorted(root.iterdir()):
            if not path.is_dir() or path.name.startswith("."):
                continue
            try:
                manifest = read_manifest(path)
            except ValueError:
                continue
            plugins.append({**manifest, "enabled":manifest["id"] not in disabled})
    return plugins


def install_plugin(source, directory):
    source, root = Path(source).expanduser(), Path(directory)
    if not source.exists() or (not source.is_dir() and source.suffix.casefold() != ".zip"):
        raise ValueError("Plugin path must be a directory or ZIP package.")
    root.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=root.parent) as temporary:
        staging = Path(temporary) / "package"
        if source.is_dir():
            shutil.copytree(source, staging)
        else:
            staging.mkdir()
            safe_zip_extract(source, staging)
        package = staging if (staging / "plugin.json").is_file() else next(
            (path for path in staging.iterdir() if path.is_dir() and (path / "plugin.json").is_file()),
            staging,
        )
        manifest = read_manifest(package)
        destination = root / manifest["id"]
        updated = destination.exists()
        if updated:
            backup = root / ".backups" / f"{manifest['id']}-{datetime.now().strftime('%Y%m%d-%H%M%S-%f')}"
            backup.parent.mkdir(parents=True, exist_ok=True)
            destination.replace(backup)
        shutil.copytree(package, destination)
    return {**manifest, "updated":updated}


def set_plugin_enabled(directory, plugin_id, enabled):
    root = Path(directory)
    manifest = read_manifest(root / plugin_id)
    state = load_plugin_state(root)
    disabled = set(state.get("disabled", []))
    disabled.discard(manifest["id"]) if enabled else disabled.add(manifest["id"])
    state["disabled"] = sorted(disabled)
    save_plugin_state(root, state)
    return enabled


def remove_plugin(directory, plugin_id):
    root = Path(directory)
    manifest = read_manifest(root / plugin_id)
    trash = root / ".removed" / f"{manifest['id']}-{datetime.now().strftime('%Y%m%d-%H%M%S-%f')}"
    trash.parent.mkdir(parents=True, exist_ok=True)
    (root / manifest["id"]).replace(trash)
    return manifest["id"]


def run_plugins(directory, hook, payload):
    result = payload
    for manifest in list_plugins(directory):
        if not manifest["enabled"] or hook not in manifest["hooks"]:
            continue
        entry = Path(directory) / manifest["id"] / manifest["entry"]
        try:
            completed = subprocess.run(
                [sys.executable, str(RUNNER), str(entry), hook],
                input=json.dumps(result), capture_output=True, text=True, timeout=5,
            )
        except (OSError, subprocess.SubprocessError):
            continue
        if completed.returncode == 0 and completed.stdout.strip():
            try:
                candidate = json.loads(completed.stdout)
                if isinstance(candidate, dict):
                    result = candidate
            except json.JSONDecodeError:
                pass
    return result
