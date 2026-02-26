#!/usr/bin/env python3
"""Créateur de clé USB bootable (style Rufus) pour MythicOS."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path


class CommandError(RuntimeError):
    """Erreur d'exécution d'une commande système."""


def run_command(cmd: list[str]) -> str:
    try:
        completed = subprocess.run(
            cmd,
            check=True,
            capture_output=True,
            text=True,
        )
    except subprocess.CalledProcessError as exc:
        stderr = exc.stderr.strip() if exc.stderr else "Erreur inconnue"
        raise CommandError(f"Commande échouée: {' '.join(cmd)}\n{stderr}") from exc
    return completed.stdout


def list_removable_devices() -> list[dict[str, str]]:
    output = run_command(["lsblk", "-J", "-o", "NAME,PATH,SIZE,MODEL,TRAN,HOTPLUG,RM,TYPE,MOUNTPOINT"])
    data = json.loads(output)
    devices: list[dict[str, str]] = []

    for device in data.get("blockdevices", []):
        is_disk = device.get("type") == "disk"
        hotplug = str(device.get("hotplug", "0")) == "1"
        removable = str(device.get("rm", "0")) == "1"
        transport = str(device.get("tran", "")) in {"usb", "mmc"}
        if is_disk and (hotplug or removable or transport):
            devices.append(
                {
                    "name": str(device.get("name", "")),
                    "path": str(device.get("path", "")),
                    "size": str(device.get("size", "")),
                    "model": str(device.get("model", "")).strip(),
                    "transport": str(device.get("tran", "")),
                    "mountpoint": str(device.get("mountpoint", "")),
                }
            )
    return devices


def verify_iso(iso_path: Path) -> tuple[bool, str]:
    if not iso_path.exists():
        return False, f"ISO introuvable: {iso_path}"
    if not iso_path.is_file():
        return False, f"Chemin invalide (pas un fichier): {iso_path}"

    output = run_command(["file", "--brief", str(iso_path)])
    if "ISO 9660" not in output and "boot" not in output.lower():
        return False, f"Le fichier ne ressemble pas à une ISO bootable: {output.strip()}"

    size_mb = iso_path.stat().st_size / (1024 * 1024)
    return True, f"ISO valide ({size_mb:.1f} MiB)"


def unmount_device_partitions(device_path: str) -> None:
    output = run_command(["lsblk", "-ln", "-o", "PATH", device_path])
    lines = [line.strip() for line in output.splitlines() if line.strip()]
    for part in lines[1:]:
        subprocess.run(["umount", part], capture_output=True, text=True)


def write_iso_to_device(iso_path: Path, device_path: str, block_size: str, sync: bool, simulate: bool) -> None:
    if simulate:
        print(f"[SIMULATION] dd if={iso_path} of={device_path} bs={block_size} status=progress conv=fsync")
        return

    if os.geteuid() != 0:
        raise PermissionError("Cette action nécessite les droits root (sudo).")

    unmount_device_partitions(device_path)

    dd_cmd = [
        "dd",
        f"if={iso_path}",
        f"of={device_path}",
        f"bs={block_size}",
        "status=progress",
        "conv=fsync",
    ]
    subprocess.run(dd_cmd, check=True)

    if sync:
        subprocess.run(["sync"], check=True)


def command_devices(_: argparse.Namespace) -> int:
    devices = list_removable_devices()
    if not devices:
        print("Aucun périphérique USB détecté.")
        return 0

    print("Périphériques USB détectés:")
    for dev in devices:
        model = dev["model"] or "inconnu"
        print(
            f"- {dev['path']} ({dev['size']}) | modèle={model} | "
            f"transport={dev['transport'] or 'n/a'}"
        )
    return 0


def command_verify(args: argparse.Namespace) -> int:
    ok, message = verify_iso(Path(args.iso))
    print(message)
    return 0 if ok else 2


def command_write(args: argparse.Namespace) -> int:
    iso_path = Path(args.iso)
    ok, message = verify_iso(iso_path)
    if not ok:
        print(message, file=sys.stderr)
        return 2

    if not Path(args.device).exists():
        print(f"Périphérique introuvable: {args.device}", file=sys.stderr)
        return 2

    print(message)
    print(f"⚠️  ATTENTION: toutes les données de {args.device} seront supprimées.")
    if not args.yes:
        confirmation = input("Tapez 'MYTHICOS' pour confirmer: ").strip()
        if confirmation != "MYTHICOS":
            print("Opération annulée.")
            return 1

    try:
        write_iso_to_device(
            iso_path=iso_path,
            device_path=args.device,
            block_size=args.block_size,
            sync=not args.no_sync,
            simulate=args.simulate,
        )
    except (PermissionError, CommandError, subprocess.CalledProcessError) as exc:
        print(f"Échec de l'écriture: {exc}", file=sys.stderr)
        return 1

    print("✅ Clé USB prête pour MythicOS.")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="mythic-usb",
        description="Créateur de clé USB bootable (style Rufus) pour MythicOS.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    devices_parser = subparsers.add_parser("devices", help="Lister les périphériques USB amovibles")
    devices_parser.set_defaults(func=command_devices)

    verify_parser = subparsers.add_parser("verify", help="Vérifier qu'un fichier ISO est valide")
    verify_parser.add_argument("iso", help="Chemin du fichier ISO MythicOS")
    verify_parser.set_defaults(func=command_verify)

    write_parser = subparsers.add_parser("write", help="Écrire une ISO sur un périphérique USB")
    write_parser.add_argument("iso", help="Chemin du fichier ISO MythicOS")
    write_parser.add_argument("device", help="Périphérique cible (ex: /dev/sdb)")
    write_parser.add_argument("--block-size", default="4M", help="Taille de bloc pour dd (défaut: 4M)")
    write_parser.add_argument("--no-sync", action="store_true", help="Ne pas forcer sync à la fin")
    write_parser.add_argument("--simulate", action="store_true", help="Simulation sans écriture disque")
    write_parser.add_argument("--yes", action="store_true", help="Confirmer automatiquement la suppression")
    write_parser.set_defaults(func=command_write)

    return parser


def check_dependencies(command: str) -> None:
    requirements = {
        "devices": ["lsblk"],
        "verify": ["file"],
        "write": ["lsblk", "file", "dd", "umount", "sync"],
    }
    required = requirements.get(command, [])
    missing = [binary for binary in required if shutil.which(binary) is None]
    if missing:
        raise EnvironmentError(
            "Dépendances manquantes: " + ", ".join(missing) + ". Installez-les puis réessayez."
        )


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    try:
        check_dependencies(args.command)
    except EnvironmentError as exc:
        print(str(exc), file=sys.stderr)
        return 3

    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
