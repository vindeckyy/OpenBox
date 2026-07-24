"""Install and configure supported Linux emulators."""

import shlex
import shutil
import subprocess


EMULATORS = {
    "org.DolphinEmu.dolphin-emu": {
        "name": "Dolphin",
        "native": "dolphin-emu",
        "profiles": {"GameCube":"-b -e {path}", "Wii":"-b -e {path}"},
    },
    "org.ppsspp.PPSSPP": {
        "name": "PPSSPP",
        "native": "ppsspp",
        "profiles": {"PSP":"{path}"},
    },
    "net.pcsx2.PCSX2": {
        "name": "PCSX2",
        "native": "pcsx2-qt",
        "profiles": {"PlayStation 2":"-batch {path}"},
    },
    "net.rpcs3.RPCS3": {
        "name": "RPCS3",
        "native": "rpcs3",
        "profiles": {"PlayStation 3":"{path}"},
    },
    "info.cemu.Cemu": {
        "name": "Cemu",
        "native": "cemu",
        "profiles": {"Wii U":"-g {path}"},
    },
    "org.mamedev.MAME": {
        "name": "MAME",
        "native": "mame",
        "profiles": {"Arcade":"{path}"},
    },
    "app.xemu.xemu": {
        "name": "xemu",
        "native": "xemu",
        "profiles": {"Xbox":"-dvd_path {path}"},
    },
}


def commands_for(app_id, prefix):
    return {
        platform: shlex.join(prefix + shlex.split(arguments))
        for platform, arguments in EMULATORS[app_id]["profiles"].items()
    }


def emulator_status(run=subprocess.run, which=shutil.which):
    flatpak = which("flatpak")
    result = []
    for app_id, emulator in EMULATORS.items():
        native = which(emulator["native"])
        flatpak_installed = bool(flatpak) and run(
            [flatpak, "info", app_id],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        ).returncode == 0
        mode = "native" if native else "flatpak" if flatpak_installed else ""
        prefix = [native] if native else [flatpak, "run", app_id] if flatpak_installed else []
        result.append({
            "app_id": app_id,
            "name": emulator["name"],
            "platforms": list(emulator["profiles"]),
            "installed": bool(mode),
            "mode": mode,
            "profiles": commands_for(app_id, prefix) if prefix else {},
            "can_install": bool(flatpak),
        })
    return result


def install_emulator(app_id, run=subprocess.run, which=shutil.which):
    if app_id not in EMULATORS:
        raise ValueError("Unknown emulator.")
    flatpak = which("flatpak")
    if not flatpak:
        raise FileNotFoundError("Flatpak is required for automatic emulator installation.")
    run(
        [flatpak, "remote-add", "--user", "--if-not-exists", "flathub", "https://flathub.org/repo/flathub.flatpakrepo"],
        check=True, capture_output=True, text=True, timeout=120,
    )
    run(
        [flatpak, "install", "--user", "--noninteractive", "-y", "flathub", app_id],
        check=True, capture_output=True, text=True, timeout=1800,
    )
    return commands_for(app_id, [flatpak, "run", app_id])
