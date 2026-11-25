# FLUMM

Hüpf-Spiel mit Pflege-Wesen (Tamagotchi-Prinzip) – Prototyp als Single-File-HTML.
Version: **v0.11.1 · Build 19**

## Apps
Android- und iOS-App über Capacitor – Builds, Signatur und Store-Upload: siehe [docs/APPS.md](docs/APPS.md).

## Spielen
`index.html` im Browser öffnen oder per GitHub Pages veröffentlichen
(Settings → Pages → Branch `main`, Ordner `/root`).

## Inhalt
- Sprungmechanik (halten = aufladen, loslassen = springen), PERFEKT-Kombos
- Abenteuer-Weltkarte (Wiesenwelt, 10 Level), Endlos, Tageslauf, Duell per Code mit Geist
- Flumm pflegen: Satt, Laune, Energie, Gesundheit, Schmutz – Werte beeinflussen sich, lange Vernachlässigung macht krank; Wachstum nach Alter + Pflege
- Erdbeeren (Futter) und Münzen (Kostüme, Designs, Medizin)
- Kostüm-Album, Gestalten (Hintergründe, 17 Plattform-Designs im eigenen SNES-3D-Stil), Endlos-Biome, Tagesgeschenk, Tutorial, Hilfe, Musik

## Nächste Schritte
- Firebase (Duelle, Freunde, Push) und Google Play Games (Erfolge, Bestenlisten)
- AdMob, weitere Welten

Spielstand liegt lokal im Browser (localStorage).

## Grafiken
Die Plattformen werden mit `tools/plattformen_generator.py` (Python + Pillow) erzeugt und als WebP in `index.html` eingebettet.
