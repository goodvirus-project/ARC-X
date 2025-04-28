#!/usr/bin/env python3
"""
ARC-X Gaming Compressor - Extractor Modul
-----------------------------------------
Dieses Modul entpackt .arcx-Archivdateien und stellt die Originalstruktur wieder her.
Es protokolliert auch die Dateigröße nach dem Entpacken.
"""

import os
import logging
import argparse
import zipfile
import json
import zstandard as zstd
import shutil
from datetime import datetime
from pathlib import Path

# Import der Hilfsfunktionen aus utils.py
from utils import format_size, get_file_category

# Konfiguration des Loggings
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('ARC-X-Extractor')

def extract_arcx_archive(arcx_file, output_dir, log_file='after_extraction.log'):
    """
    Entpackt eine .arcx-Archivdatei und stellt die Originalstruktur wieder her.
    
    Args:
        arcx_file (str): Pfad zur .arcx-Archivdatei
        output_dir (str): Pfad zum Ausgabeverzeichnis
        log_file (str, optional): Pfad zur Log-Datei
    
    Returns:
        dict: Statistik über die extrahierten Dateien
    """
    logger.info(f"Starte Entpacken des ARCX-Archivs: {arcx_file}")
    
    # Überprüfen, ob die Archivdatei existiert
    if not os.path.isfile(arcx_file):
        raise FileNotFoundError(f"Die Archivdatei {arcx_file} existiert nicht.")
    
    # Sicherstellen, dass das Ausgabeverzeichnis existiert
    os.makedirs(output_dir, exist_ok=True)
    
    # Statistik initialisieren
    stats = {
        'total_files': 0,
        'total_size': 0,
        'categories': {
            'Textur': {'count': 0, 'size': 0},
            'Audio': {'count': 0, 'size': 0},
            'Modell': {'count': 0, 'size': 0},
            'Script': {'count': 0, 'size': 0},
            'Sonstige': {'count': 0, 'size': 0}
        }
    }
    
    # Temporäres Verzeichnis für die Extraktion erstellen
    import tempfile
    temp_dir = tempfile.mkdtemp(prefix="arcx_extract_")
    
    try:
        # Log-Datei erstellen
        with open(log_file, 'w', encoding='utf-8') as f:
            f.write("ARC-X Gaming Compressor - Extraktionsergebnisse\n")
            f.write(f"Datum: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Archivdatei: {arcx_file}\n")
            f.write(f"Ausgabeverzeichnis: {output_dir}\n")
            f.write("-" * 80 + "\n")
            f.write(f"{'Dateipfad':<60} {'Kategorie':<15} {'Größe':<15}\n")
            f.write("-" * 80 + "\n")
        
        # ZIP-Archiv entpacken
        with zipfile.ZipFile(arcx_file, 'r') as zipf:
            # Zuerst die Metadaten extrahieren
            zipf.extract("arcx_metadata.json", temp_dir)
            
            # Metadaten lesen
            metadata_path = os.path.join(temp_dir, "arcx_metadata.json")
            with open(metadata_path, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
            
            logger.info(f"ARCX-Archiv Version: {metadata.get('version', 'unbekannt')}")
            logger.info(f"Erstellt am: {metadata.get('created', 'unbekannt')}")
            logger.info(f"Komprimierungsstufe: {metadata.get('compression_level', 'unbekannt')}")
            
            # Alle Dateien extrahieren
            zipf.extractall(temp_dir)
        
        # Zstandard-Dekompressor erstellen
        dctx = zstd.ZstdDecompressor()
        
        # Alle Dateien entpacken
        for file_info in metadata['files']:
            rel_path = file_info['path']
            category = file_info['category']
            
            # Pfad zur komprimierten Datei im temporären Verzeichnis
            compressed_path = os.path.join(temp_dir, rel_path + '.zst')
            
            # Ausgabepfad im Zielverzeichnis
            output_path = os.path.join(output_dir, rel_path)
            
            # Sicherstellen, dass das Zielverzeichnis existiert
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            try:
                # Datei dekomprimieren
                with open(compressed_path, 'rb') as f_in:
                    with open(output_path, 'wb') as f_out:
                        decompressor = dctx.stream_reader(f_in)
                        shutil.copyfileobj(decompressor, f_out)
                
                # Größe der entpackten Datei ermitteln
                file_size = os.path.getsize(output_path)
                
                # Statistik aktualisieren
                stats['total_files'] += 1
                stats['total_size'] += file_size
                stats['categories'][category]['count'] += 1
                stats['categories'][category]['size'] += file_size
                
                # In Log-Datei schreiben
                with open(log_file, 'a', encoding='utf-8') as f:
                    formatted_size = format_size(file_size)
                    f.write(f"{rel_path:<60} {category:<15} {formatted_size:<15}\n")
                
                logger.info(f"Datei entpackt: {rel_path} ({formatted_size})")
                
            except Exception as e:
                logger.error(f"Fehler beim Entpacken von {rel_path}: {e}")
        
        # Zusammenfassung in Log-Datei schreiben
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write("\n" + "-" * 80 + "\n")
            f.write("ZUSAMMENFASSUNG\n")
            f.write("-" * 80 + "\n")
            f.write(f"Gesamtanzahl Dateien: {stats['total_files']}\n")
            f.write(f"Gesamtgröße: {format_size(stats['total_size'])}\n\n")
            
            f.write("Aufschlüsselung nach Kategorien:\n")
            for category, data in stats['categories'].items():
                if data['count'] > 0:  # Nur Kategorien anzeigen, die Dateien enthalten
                    f.write(f"{category}: {data['count']} Dateien, {format_size(data['size'])}\n")
        
        logger.info(f"Entpacken abgeschlossen. {stats['total_files']} Dateien extrahiert.")
        logger.info(f"Ergebnisse wurden in {log_file} gespeichert.")
        
        return stats
    
    finally:
        # Temporäres Verzeichnis aufräumen
        shutil.rmtree(temp_dir, ignore_errors=True)

def main():
    """
    Hauptfunktion des Programms.
    """
    parser = argparse.ArgumentParser(description='ARC-X Gaming Compressor - Extractor')
    parser.add_argument('arcx_file', help='Name der .arcx-Archivdatei (wird im compressed/ Ordner gesucht)')
    parser.add_argument('--output', default='extracted', help='Ausgabeverzeichnis (Standard: extracted)')
    parser.add_argument('--log', default='after_extraction.log', help='Pfad zur Log-Datei (Standard: after_extraction.log)')
    parser.add_argument('--compressed-dir', default='compressed', help='Verzeichnis, in dem die .arcx-Dateien gespeichert sind (Standard: compressed)')
    
    args = parser.parse_args()
    
    # Pfad zur Archivdatei im compressed/ Ordner erstellen
    arcx_name = args.arcx_file
    if not arcx_name.endswith('.arcx'):
        arcx_name += '.arcx'
    
    compressed_dir = args.compressed_dir
    if not os.path.isabs(compressed_dir):
        compressed_dir = os.path.join(os.getcwd(), compressed_dir)
    
    arcx_path = os.path.join(compressed_dir, arcx_name)
    
    # Überprüfen, ob die angegebene Archivdatei existiert
    if not os.path.isfile(arcx_path):
        logger.error(f"Die angegebene Archivdatei existiert nicht: {arcx_path}")
        logger.info(f"Bitte stellen Sie sicher, dass die Datei im Verzeichnis {compressed_dir} vorhanden ist.")
        return
    
    # Absoluten Pfad für die Log-Datei erstellen
    log_path = args.log
    if not os.path.isabs(log_path):
        log_path = os.path.join(os.getcwd(), log_path)
    
    # Absoluten Pfad für das Ausgabeverzeichnis erstellen
    output_dir = args.output
    if not os.path.isabs(output_dir):
        output_dir = os.path.join(os.getcwd(), output_dir)
    
    # Archiv entpacken
    try:
        logger.info(f"Entpacke Archiv: {arcx_path}")
        extract_arcx_archive(arcx_path, output_dir, log_path)
    except Exception as e:
        logger.error(f"Fehler beim Entpacken des Archivs: {e}")

if __name__ == "__main__":
    main()