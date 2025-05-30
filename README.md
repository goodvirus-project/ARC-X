<div align="center">
  <img src="image/ARC-X-Logo.png" alt="ARC-X Gaming Compressor Logo" width="300">
  <p><em>Logo ist ein vorläufiger Platzhalter</em></p>
</div>

# ARC-X Gaming Compressor

Ein leistungsstarkes Werkzeug zum Scannen, Komprimieren und Entpacken von Spieledateien mit Multithreading-Unterstützung.

## Dokumentation

Die vollständige Dokumentation ist in folgenden Sprachen verfügbar:
- [Deutsch](docs/README.de.md)
- [English](docs/README.en.md)

## Kurzbeschreibung

Der ARC-X Gaming Compressor ist ein fortschrittliches Werkzeug, das Spieledateien effizient komprimieren und verwalten kann. Es kategorisiert Dateien nach Typ und verwendet den Zstandard-Kompressionsalgorithmus für optimale Kompressionsraten. Die Multithreading-Unterstützung ermöglicht eine deutlich schnellere Verarbeitung großer Spieleverzeichnisse.

### Hauptfunktionen

- Spielespezifische Dateierkennung und intelligente Kompressionsstrategien
- Multithreaded-Architektur für schnellere Kompression
- Robuste Fehlerbehandlung und detaillierte Protokollierung
- Bis zu 30% Platzersparnis bei typischen Spieledaten

## Schnellstart

```bash
# Repository klonen
git clone https://github.com/yourusername/ARC-X.git
cd ARC-X

# Abhängigkeiten installieren
pip install -r requirements.txt

# Spieleverzeichnis komprimieren (mit 8 Threads)
python src/compressor.py --input "C:/Games/MyGame" --output "compressed/mygame.arcx" --threads 8

# Archiv entpacken
python src/extractor.py --input "compressed/mygame.arcx" --output "C:/Games/MyGame_Extracted"
