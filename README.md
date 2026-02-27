# MythicOS USB Creator

Application **publishable** pour créer une clé USB bootable MythicOS, inspirée de Rufus.

## Ce qui est inclus

- **CLI** : `mythic-usb`
- **GUI lançable** : `mythic-usb-gui` (Tkinter)
- **Entrée desktop** : `mythic-usb.desktop`
- **Icône** : `mythic-usb.svg`
- **Packaging Debian source complet** (`debian/`)
- **Autopkgtests** (`debian/tests/`)

## Fonctionnalités

- Détection des périphériques USB amovibles
- Vérification d'une image ISO
- Écriture de l'ISO vers USB avec garde-fous
- Mode simulation
- Sortie JSON (`devices --json`) pour intégration GUI/scripts

## Utilisation CLI

```bash
mythic-usb --version
mythic-usb devices
mythic-usb devices --json
mythic-usb verify /chemin/MythicOS.iso
sudo mythic-usb write /chemin/MythicOS.iso /dev/sdX --yes
```

## Utilisation GUI

```bash
mythic-usb-gui
```

La GUI lance automatiquement `mythic-usb` installé (ou fallback script local en dev), et utilise `pkexec` pour l'écriture réelle si nécessaire.

## Build Debian

```bash
dpkg-buildpackage -S -us -uc   # paquet source
dpkg-buildpackage -b -us -uc   # paquet binaire local
```

## Fichiers installés

- `/usr/bin/mythic-usb`
- `/usr/bin/mythic-usb-gui`
- `/usr/share/applications/mythic-usb.desktop`
- `/usr/share/icons/hicolor/scalable/apps/mythic-usb.svg`

## Sécurité

- Vérifie toujours le périphérique cible.
- N'écris jamais sur le disque système.
- Sauvegarde les données de la clé avant écriture.
