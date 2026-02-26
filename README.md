# MythicOS USB Creator

Application pour créer une clé USB bootable MythicOS, inspirée de l'approche Rufus.

## Ce qui est inclus

- **CLI**: `mythic-usb` (detection, verify, write)
- **GUI lançable**: `mythic-usb-gui` (interface Tkinter)
- **Icône d'application** installée dans le thème `hicolor`
- **Entrée desktop**: "MythicOS USB Creator"
- **Paquet Debian source complet** dans `debian/`

## Fonctionnalités CLI

- Détection des périphériques USB amovibles (`devices`)
- Vérification d'une image ISO (`verify`)
- Écriture de l'ISO sur une clé USB (`write`)
- Mode simulation pour tester la commande sans toucher au disque

## Utilisation rapide CLI

```bash
# Lister les clés USB détectées
mythic-usb devices

# Vérifier une ISO MythicOS
mythic-usb verify /chemin/MythicOS.iso

# Écrire l'ISO (⚠️ efface la clé)
sudo mythic-usb write /chemin/MythicOS.iso /dev/sdX
```

## Utilisation GUI

```bash
mythic-usb-gui
```

Ou via le menu d'applications avec l'icône **MythicOS USB Creator**.

## Build Debian

### Construire le paquet source

```bash
dpkg-buildpackage -S -us -uc
```

### Construire le paquet binaire local

```bash
dpkg-buildpackage -b -us -uc
```

Le paquet installe:

- `/usr/bin/mythic-usb`
- `/usr/bin/mythic-usb-gui`
- `/usr/share/applications/mythic-usb.desktop`
- `/usr/share/icons/hicolor/scalable/apps/mythic-usb.svg`

## Conseils de sécurité

- Vérifie toujours le bon périphérique (`/dev/sdb`, `/dev/sdc`, etc.) avant écriture.
- N'utilise jamais le disque système (`/dev/sda`) comme destination.
- Fais une sauvegarde des données de la clé avant d'écrire l'image.
