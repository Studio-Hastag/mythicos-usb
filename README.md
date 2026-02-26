# MythicOS USB Creator

Un utilitaire en ligne de commande pour créer une clé USB bootable MythicOS, inspiré de l'approche de Rufus (détection de clé + écriture d'ISO).

## Fonctionnalités

- Détection des périphériques USB amovibles (`devices`)
- Vérification d'une image ISO (`verify`)
- Écriture de l'ISO sur une clé USB (`write`)
- Mode simulation pour tester la commande sans toucher au disque

## Prérequis

- Linux
- Python 3.10+
- Outils système: `lsblk`, `file`, `dd`, `umount`, `sync`

## Utilisation rapide

```bash
# 1) Voir les clés USB détectées
./mythic_usb_creator.py devices

# 2) Vérifier l'ISO MythicOS
./mythic_usb_creator.py verify /chemin/MythicOS.iso

# 3) Écrire l'ISO (⚠️ efface la clé)
sudo ./mythic_usb_creator.py write /chemin/MythicOS.iso /dev/sdX
```

## Exemples

### Simulation (sans écriture)

```bash
./mythic_usb_creator.py write ./MythicOS.iso /dev/sdb --simulate --yes
```

### Écriture réelle avec confirmation automatique

```bash
sudo ./mythic_usb_creator.py write ./MythicOS.iso /dev/sdb --yes
```

## Paquet Debian source

Le dépôt inclut maintenant un empaquetage Debian source complet dans `debian/`.

### Construire le paquet source

```bash
dpkg-buildpackage -S -us -uc
```

### Construire le paquet binaire local

```bash
dpkg-buildpackage -b -us -uc
```

Le binaire installe la commande sous:

```bash
/usr/bin/mythic-usb
```

## Conseils de sécurité

- Vérifie toujours le bon périphérique (`/dev/sdb`, `/dev/sdc`, etc.) avant écriture.
- N'utilise jamais le disque système (`/dev/sda`) comme destination.
- Fais une sauvegarde des données de la clé avant d'écrire l'image.

## Limites actuelles

- Outil CLI uniquement (pas encore d'interface graphique).
- Écriture brute via `dd` (comme beaucoup d'outils Linux classiques).
- Le script suppose une ISO hybride/bootable standard.

## Idées d'amélioration

- Interface graphique (GTK/Qt) style Rufus.
- Vérification de checksum SHA256 des ISO.
- Téléchargement automatique des versions MythicOS.
- Journal d'installation détaillé.
