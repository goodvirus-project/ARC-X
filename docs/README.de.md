<div align="center">
  <img src="../image/ARC-X-Logo.png" alt="ARC-X Gaming Compressor Logo" width="300">
  <p><em>Logo ist ein vorläufiger Platzhalter</em></p>
</div>

# ARC-X Gaming Compressor

Ein leistungsstarkes Werkzeug zum Scannen, Komprimieren und Entpacken von Spieledateien mit Multithreading-Unterstützung.

[English version](README.en.md)

## Beschreibung

Der ARC-X Gaming Compressor ist ein fortschrittliches Werkzeug, das Spieledateien effizient komprimieren und verwalten kann. Es kategorisiert Dateien nach Typ (Texturen, Audio, 3D-Modelle, Scripts) und verwendet den Zstandard-Kompressionsalgorithmus für optimale Kompressionsraten. Die neue Multithreading-Unterstützung ermöglicht eine deutlich schnellere Verarbeitung großer Spieleverzeichnisse.

### Vergleich mit herkömmlichen Kompressionstools

Auf den ersten Blick mag ARC-X an allgemeine Kompressionstools wie 7-Zip oder WinRAR erinnern, aber es wurde speziell für die Anforderungen moderner Spiele entwickelt und bietet mehrere entscheidende Vorteile:

- **Spielespezifische Dateierkennung**: Erkennt und kategorisiert automatisch verschiedene Spieledateitypen für optimale Kompression
- **Intelligente Kompressionsstrategien**: Wendet unterschiedliche Kompressionseinstellungen basierend auf dem Dateityp an
- **Für große Spieleverzeichnisse optimiert**: Speziell entwickelt, um mit den umfangreichen Datenmengen moderner Spiele umzugehen
- **Multithreaded-Architektur**: Nutzt die volle Leistung moderner Mehrkernprozessoren für schnellere Kompression
- **Spieleentwickler-freundlich**: Bietet detaillierte Analysen und Protokolle, die für Spieleentwickler und Publisher wertvoll sind

ARC-X wurde von Grund auf für die Gaming-Branche entwickelt und konzentriert sich auf die spezifischen Herausforderungen bei der Komprimierung von Spieledateien, anstatt eine Universallösung für alle Arten von Daten zu sein.

## Funktionen

- **Verzeichnisscanner**: Durchsucht Verzeichnisse rekursiv und kategorisiert Dateien
- **Multithreaded Kompressor**: Komprimiert Dateien parallel mit mehreren Threads für maximale Geschwindigkeit
- **Robuste Fehlerbehandlung**: Setzt die Komprimierung auch bei Problemen mit einzelnen Dateien fort
- **Fortschrittsanzeige**: Zeigt Echtzeit-Fortschritt mit geschätzter verbleibender Zeit
- **Extraktor**: Entpackt .arcx-Archive und stellt die Originalstruktur wieder her
- **Detaillierte Protokollierung**: Erstellt ausführliche Logs über Dateigröße und Kompressionsrate
- **Fehlerprotokollierung**: Speichert detaillierte Informationen zu fehlgeschlagenen Dateien

## Neue Funktionen

- **Multithreaded Komprimierung**: Bis zu 10x schnellere Verarbeitung durch parallele Komprimierung
- **Verbesserte Fehlerbehandlung**: Robuste Verarbeitung auch bei Problemen mit einzelnen Dateien
- **Fortschrittsanzeige in Echtzeit**: Zeigt Prozentsatz, verbleibende Zeit und Fehleranzahl
- **Detaillierte Fehlerprotokolle**: Separate Protokolldatei für fehlgeschlagene Dateien
- **Optimierte Speichernutzung**: Effiziente Verarbeitung auch bei sehr großen Spieleverzeichnissen

> **Hinweis**: Einige der fortgeschrittenen Funktionen befinden sich noch in der Entwicklung und werden in zukünftigen Updates verfügbar sein. Die Kernfunktionalität der multithreaded Komprimierung und verbesserten Fehlerbehandlung ist bereits vollständig implementiert.

## Kompressionsbeispiele

| Dateityp | Typische Kompressionsrate | Platzersparnis |
|----------|---------------------------|----------------|
| Skriptdateien | 5.6x | 82% |
| DLL-Dateien | 2.5x | 60% |
| Ausführbare Dateien | 2.4x | 58% |
| Textdateien | 3.1x | 68% |
| Unkomprimierte Texturen | 2.2x | 55% |
| Bereits komprimierte Dateien | 1.0-1.1x | 0-10% |

**Beispiel für 100 GB Spieledaten:**
- Skriptdateien (5 GB): Reduziert auf 0.9 GB (Ersparnis: 4.1 GB)
- DLL-Dateien (10 GB): Reduziert auf 4 GB (Ersparnis: 6 GB)
- Ausführbare Dateien (2 GB): Reduziert auf 0.8 GB (Ersparnis: 1.2 GB)
- Unkomprimierte Texturen (30 GB): Reduziert auf 13.6 GB (Ersparnis: 16.4 GB)
- Bereits komprimierte Dateien (53 GB): Reduziert auf 50.4 GB (Ersparnis: 2.6 GB)
- **Gesamtersparnis: 30.3 GB (30.3% weniger Speicherplatz)**

## Installation

1. Klonen Sie das Repository:
   ```
   git clone https://github.com/yourusername/ARC-X.git
   cd ARC-X
   ```

2. Installieren Sie die Abhängigkeiten:
   ```
   pip install -r requirements.txt
   ```

## Verwendung

### Verzeichnis scannen

```
python src/compressor.py <verzeichnis>
```

Erstellt eine `before_compression.log` Datei mit Informationen über alle gefundenen Dateien.

### Verzeichnis komprimieren (Einzelthread)

```
python src/compressor.py <verzeichnis> --compress [--output <n>] [--level <1-22>]
```

### Verzeichnis komprimieren (Multithreaded)

```
python src/compressor.py <verzeichnis> --compress --multithreaded [--threads <anzahl>] [--output <n>] [--level <1-22>]
```

Komprimiert alle Dateien im angegebenen Verzeichnis parallel und erstellt ein .arcx-Archiv im `compressed/` Ordner.

### Archiv entpacken

```
python src/extractor.py <n> [--output <ausgabeverzeichnis>]
```

Entpackt ein .arcx-Archiv aus dem `compressed/` Ordner in das angegebene Ausgabeverzeichnis.

## Projektstruktur

```
├── src/
│   ├── compressor.py  # Hauptmodul zum Scannen und Komprimieren
│   ├── extractor.py   # Modul zum Entpacken von .arcx-Archiven
│   ├── utils.py       # Hilfsfunktionen für Dateierkennung und -verarbeitung
├── compressed/        # Ausgabeverzeichnis für komprimierte Archive
├── docs/              # Dokumentation
├── requirements.txt   # Abhängigkeiten
└── README.md          # Kurze Übersicht und Verweis auf die Dokumentation
```

> **Hinweis zur Entwicklung**: Die aktuelle Version von ARC-X ist als Testversion in nur drei Hauptdateien implementiert. In zukünftigen Versionen wird die Codestruktur verbessert und modularisiert, um eine bessere Wartbarkeit und Erweiterbarkeit zu gewährleisten. Die einfache Struktur der aktuellen Version ermöglicht schnelles Testen und Iterieren der Kernfunktionalitäten.

## Abhängigkeiten

- Python 3.6+
- zstandard
- concurrent.futures (Standard-Bibliothek)

## Lizenz

Dieses Projekt ist unter der MIT-Lizenz lizenziert - siehe die [LICENSE](../LICENSE) Datei für Details.

## Mitwirken

Beiträge sind willkommen! Bitte lesen Sie [CONTRIBUTING.md](CONTRIBUTING.de.md) für Details zu unserem Verhaltenskodex und dem Prozess für das Einreichen von Pull Requests.

## Danksagungen

- Die Zstandard-Kompressionsbibliothek
- Alle Mitwirkenden, die bei Tests und Entwicklung geholfen haben