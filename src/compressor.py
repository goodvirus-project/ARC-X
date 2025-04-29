#!/usr/bin/env python3
"""
ARC-X Gaming Compressor - Grundmodul
-----------------------------------
Dieses Modul durchsucht einen angegebenen Ordner rekursiv,
kategorisiert alle gefundenen Dateien und protokolliert ihre Größe.
Es bietet auch Funktionen zum Komprimieren von Dateien mit Zstandard.
"""

import os
import logging
import argparse
import shutil
import zstandard as zstd
import threading
import queue
import time
from concurrent.futures import ThreadPoolExecutor, wait
from pathlib import Path
from datetime import datetime

# Import der Hilfsfunktionen aus utils.py
from utils import (
    is_texture, is_audio, is_model, is_script,
    get_file_size, get_file_category, format_size,
    get_compression_level_by_type
)

# Konfiguration des Loggings
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('ARC-X')

def scan_directory(directory_path, log_file):
    """
    Durchsucht einen Ordner rekursiv und protokolliert alle gefundenen Dateien.
    
    Args:
        directory_path (str): Pfad zum zu durchsuchenden Ordner
        log_file (str): Pfad zur Log-Datei
    """
    logger.info(f"Starte Scan des Verzeichnisses: {directory_path}")
    
    # Erstelle Log-Datei und schreibe Header
    with open(log_file, 'w', encoding='utf-8') as f:
        f.write("ARC-X Gaming Compressor - Scan-Ergebnis\n")
        f.write(f"Datum: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Durchsuchtes Verzeichnis: {directory_path}\n")
        f.write("-" * 80 + "\n")
        f.write(f"{'Dateipfad':<60} {'Kategorie':<15} {'Größe':<15}\n")
        f.write("-" * 80 + "\n")
    
    # Statistik-Zähler
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
    
    # Rekursive Durchsuchung des Verzeichnisses
    for root, _, files in os.walk(directory_path):
        for file in files:
            file_path = os.path.join(root, file)
            
            try:
                # Dateigröße ermitteln in Bytes
                file_size_bytes = os.path.getsize(file_path)
                # Dateigröße in MB für die Anzeige
                file_size_mb = get_file_size(file_path)
                
                # Kategorie bestimmen mit den Hilfsfunktionen
                if is_texture(file_path):
                    category = "Textur"
                elif is_audio(file_path):
                    category = "Audio"
                elif is_model(file_path):
                    category = "Modell"
                elif is_script(file_path):
                    category = "Script"
                else:
                    category = "Sonstige"
                
                # Statistik aktualisieren
                stats['total_files'] += 1
                stats['total_size'] += file_size_bytes
                stats['categories'][category]['count'] += 1
                stats['categories'][category]['size'] += file_size_bytes
                
                # In Log-Datei schreiben
                with open(log_file, 'a', encoding='utf-8') as f:
                    relative_path = os.path.relpath(file_path, directory_path)
                    formatted_size = format_size(file_size_bytes)
                    f.write(f"{relative_path:<60} {category:<15} {formatted_size:<15}\n")
                
            except Exception as e:
                logger.error(f"Fehler beim Verarbeiten von {file_path}: {e}")
    
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
    
    logger.info(f"Scan abgeschlossen. {stats['total_files']} Dateien gefunden.")
    logger.info(f"Ergebnisse wurden in {log_file} gespeichert.")
    
    return stats

def compress_file(file_path, output_path, compression_level=None):
    """
    Komprimiert eine Datei mit Zstandard und speichert sie im Zielordner.
    
    Args:
        file_path (str): Pfad zur zu komprimierenden Datei
        output_path (str): Pfad, unter dem die komprimierte Datei gespeichert werden soll
        compression_level (int, optional): Komprimierungsstufe (1-22, höher = stärkere Kompression, langsamer)
                                          Wenn None, wird der optimale Level basierend auf dem Dateityp bestimmt
    
    Returns:
        tuple: (original_size, compressed_size, compression_ratio)
    
    Raises:
        FileNotFoundError: Wenn die Quelldatei nicht existiert
        PermissionError: Wenn keine Berechtigung zum Lesen/Schreiben besteht
    """
    try:
        # Überprüfen, ob die Quelldatei existiert
        if not os.path.isfile(file_path):
            raise FileNotFoundError(f"Die Datei {file_path} existiert nicht.")
        
        # Sicherstellen, dass das Zielverzeichnis existiert
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Originalgröße ermitteln
        original_size = os.path.getsize(file_path)
        
        # Wenn kein Kompressionslevel angegeben wurde, optimalen Level basierend auf Dateityp bestimmen
        if compression_level is None:
            compression_level = get_compression_level_by_type(file_path)
            file_type = "unknown"
            if is_script(file_path):
                file_type = "script"
            elif is_texture(file_path):
                file_type = "texture"
            elif is_audio(file_path):
                file_type = "audio"
            elif is_model(file_path):
                file_type = "model"
            else:
                file_type = "other"
            
            logger.info(f"Compressing {file_path} with level {compression_level} due to type {file_type}")
        else:
            logger.info(f"Compressing {file_path} with manually set level {compression_level}")
        
        # Zstandard-Kompressor mit bestimmtem Kompressionslevel erstellen
        cctx = zstd.ZstdCompressor(level=compression_level)
        
        # Datei komprimieren
        with open(file_path, 'rb') as f_in:
            with open(output_path, 'wb') as f_out:
                compressor = cctx.stream_writer(f_out)
                shutil.copyfileobj(f_in, compressor)
                compressor.close()
        
        # Größe der komprimierten Datei ermitteln
        compressed_size = os.path.getsize(output_path)
        
        # Kompressionsrate berechnen (Original / Komprimiert)
        compression_ratio = original_size / compressed_size if compressed_size > 0 else 0
        
        logger.info(f"Datei komprimiert: {file_path} -> {output_path}")
        logger.info(f"Originalgröße: {format_size(original_size)}, Komprimierte Größe: {format_size(compressed_size)}")
        logger.info(f"Kompressionsrate: {compression_ratio:.2f}x")
        
        return (original_size, compressed_size, compression_ratio)
    
    except Exception as e:
        logger.error(f"Fehler beim Komprimieren von {file_path}: {e}")
        raise

def create_arcx_archive(input_dir, output_file, compression_level=None, log_file='compression_results.log'):
    """
    Erstellt eine .arcx-Archivdatei aus einem Verzeichnis.
    
    Args:
        input_dir (str): Pfad zum Quellverzeichnis
        output_file (str): Pfad zur Ausgabe-Archivdatei (.arcx)
        compression_level (int, optional): Komprimierungsstufe (1-22)
                                          Wenn None, wird der optimale Level für jeden Dateityp automatisch bestimmt
        log_file (str, optional): Pfad zur Log-Datei
    
    Returns:
        dict: Statistik über die Komprimierung
    """
    logger.info(f"Starte Erstellung des ARCX-Archivs aus: {input_dir}")
    
    # Sicherstellen, dass das Ausgabeverzeichnis existiert
    os.makedirs(os.path.dirname(os.path.abspath(output_file)), exist_ok=True)
    
    # Statistik initialisieren
    stats = {
        'total_files': 0,
        'total_original_size': 0,
        'total_compressed_size': 0,
        'categories': {
            'Textur': {'count': 0, 'original_size': 0, 'compressed_size': 0},
            'Audio': {'count': 0, 'original_size': 0, 'compressed_size': 0},
            'Modell': {'count': 0, 'original_size': 0, 'compressed_size': 0},
            'Script': {'count': 0, 'original_size': 0, 'compressed_size': 0},
            'Sonstige': {'count': 0, 'original_size': 0, 'compressed_size': 0}
        }
    }
    
    # Temporäres Verzeichnis für komprimierte Dateien erstellen
    import tempfile
    temp_dir = tempfile.mkdtemp(prefix="arcx_temp_")
    
    try:
        # Log-Datei erstellen
        with open(log_file, 'w', encoding='utf-8') as f:
            f.write("ARC-X Gaming Compressor - Komprimierungsergebnisse\n")
            f.write(f"Datum: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Quellverzeichnis: {input_dir}\n")
            f.write(f"Ausgabe-Archiv: {output_file}\n")
            
            if compression_level is None:
                f.write("Komprimierungsstufe: Automatisch (basierend auf Dateityp)\n")
                f.write("  - Skripte (.txt, .json, .xml, .lua): Level 12\n")
                f.write("  - Texturen (.png, .jpg, .dds): Level 5\n")
                f.write("  - Audiodateien (.wav, .ogg, .mp3): Level 2\n")
                f.write("  - 3D-Modelle (.fbx, .obj, .dae): Level 6\n")
                f.write("  - Alle anderen: Level 3\n")
            else:
                f.write(f"Komprimierungsstufe: {compression_level} (manuell festgelegt)\n")
                
            f.write("-" * 120 + "\n")
            f.write("KOMPRESSIONSDETAILS:\n")
            f.write("-" * 120 + "\n")
            f.write(f"{'Dateipfad':<50} {'Kategorie':<10} {'Original':<15} {'Komprimiert':<15} {'Ratio':<20}\n")
            f.write("-" * 120 + "\n")
        
        # Metadaten-Datei für das Archiv erstellen
        metadata = {
            'version': '1.0',
            'created': datetime.now().isoformat(),
            'compression_mode': 'automatic_by_type' if compression_level is None else 'manual',
            'compression_level': compression_level,
            'files': []
        }
        
        # Rekursive Durchsuchung des Verzeichnisses
        for root, _, files in os.walk(input_dir):
            for file in files:
                file_path = os.path.join(root, file)
                
                # Relativen Pfad berechnen
                rel_path = os.path.relpath(file_path, input_dir)
                
                # Ausgabepfad im temporären Verzeichnis erstellen
                temp_output_path = os.path.join(temp_dir, rel_path + '.zst')
                os.makedirs(os.path.dirname(temp_output_path), exist_ok=True)
                
                try:
                    # Kategorie bestimmen
                    if is_texture(file_path):
                        category = "Textur"
                    elif is_audio(file_path):
                        category = "Audio"
                    elif is_model(file_path):
                        category = "Modell"
                    elif is_script(file_path):
                        category = "Script"
                    else:
                        category = "Sonstige"
                    
                    # Bestimme den Kompressionslevel für diese Datei
                    file_compression_level = compression_level
                    if file_compression_level is None:
                        file_compression_level = get_compression_level_by_type(file_path)
                        
                        # Bestimme den Dateityp für den Log-Eintrag
                        file_type = "other"
                        if is_script(file_path):
                            file_type = "script"
                        elif is_texture(file_path):
                            file_type = "texture"
                        elif is_audio(file_path):
                            file_type = "audio"
                        elif is_model(file_path):
                            file_type = "model"
                        
                        # Schreibe die Entscheidung in die Log-Datei
                        with open(log_file, 'a', encoding='utf-8') as f:
                            f.write(f"INFO: Compressing {rel_path} with level {file_compression_level} due to type {file_type}\n")
                    
                    # Datei komprimieren
                    original_size, compressed_size, ratio = compress_file(file_path, temp_output_path, file_compression_level)
                    
                    # Metadaten für diese Datei hinzufügen
                    metadata['files'].append({
                        'path': rel_path,
                        'category': category,
                        'compression_level': file_compression_level,
                        'original_size': original_size,
                        'compressed_size': compressed_size
                    })
                    
                    # Statistik aktualisieren
                    stats['total_files'] += 1
                    stats['total_original_size'] += original_size
                    stats['total_compressed_size'] += compressed_size
                    stats['categories'][category]['count'] += 1
                    stats['categories'][category]['original_size'] += original_size
                    stats['categories'][category]['compressed_size'] += compressed_size
                    
                    # In Log-Datei schreiben
                    with open(log_file, 'a', encoding='utf-8') as f:
                        f.write(f"{rel_path:<50} {category:<10} {format_size(original_size):<15} "
                                f"{format_size(compressed_size):<15} {ratio:.2f}x (Level {file_compression_level})\n")
                    
                except Exception as e:
                    logger.error(f"Fehler beim Komprimieren von {file_path}: {e}")
        
        # Metadaten als JSON in temporäres Verzeichnis schreiben
        import json
        metadata_path = os.path.join(temp_dir, "arcx_metadata.json")
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2)
        
        # Alle komprimierten Dateien und Metadaten in ein ZIP-Archiv packen
        import zipfile
        with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Zuerst die Metadaten hinzufügen
            zipf.write(metadata_path, "arcx_metadata.json")
            
            # Dann alle komprimierten Dateien
            for root, _, files in os.walk(temp_dir):
                for file in files:
                    if file == "arcx_metadata.json":
                        continue  # Metadaten haben wir bereits hinzugefügt
                    
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, temp_dir)
                    zipf.write(file_path, arcname)
        
        # Zusammenfassung in Log-Datei schreiben
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write("\n" + "-" * 120 + "\n")
            f.write("ZUSAMMENFASSUNG\n")
            f.write("-" * 120 + "\n")
            
            if compression_level is None:
                f.write("Verwendete Kompressionsstrategie: Automatisch basierend auf Dateityp\n")
                f.write("  - Skripte: Level 12\n")
                f.write("  - Texturen: Level 5\n")
                f.write("  - Audiodateien: Level 2\n")
                f.write("  - 3D-Modelle: Level 6\n")
                f.write("  - Andere Dateien: Level 3\n\n")
            else:
                f.write(f"Verwendete Kompressionsstrategie: Manuell festgelegter Level {compression_level} für alle Dateien\n\n")
            f.write(f"Gesamtanzahl Dateien: {stats['total_files']}\n")
            
            if stats['total_compressed_size'] > 0:
                overall_ratio = stats['total_original_size'] / stats['total_compressed_size']
            else:
                overall_ratio = 0
                
            f.write(f"Gesamtgröße (Original): {format_size(stats['total_original_size'])}\n")
            f.write(f"Gesamtgröße (Komprimiert): {format_size(stats['total_compressed_size'])}\n")
            f.write(f"Gesamtersparnis: {format_size(stats['total_original_size'] - stats['total_compressed_size'])}\n")
            f.write(f"Durchschnittliche Kompressionsrate: {overall_ratio:.2f}x\n\n")
            
            f.write("Aufschlüsselung nach Kategorien:\n")
            for category, data in stats['categories'].items():
                if data['count'] > 0:
                    if data['compressed_size'] > 0:
                        cat_ratio = data['original_size'] / data['compressed_size']
                    else:
                        cat_ratio = 0
                        
                    f.write(f"{category}: {data['count']} Dateien, "
                            f"Original: {format_size(data['original_size'])}, "
                            f"Komprimiert: {format_size(data['compressed_size'])}, "
                            f"Ratio: {cat_ratio:.2f}x\n")
        
        # Größe der finalen ARCX-Datei ermitteln
        arcx_size = os.path.getsize(output_file)
        logger.info(f"ARCX-Archiv erstellt: {output_file} ({format_size(arcx_size)})")
        logger.info(f"Komprimierung abgeschlossen. {stats['total_files']} Dateien komprimiert.")
        logger.info(f"Ergebnisse wurden in {log_file} gespeichert.")
        
        return stats
    
    finally:
        # Temporäres Verzeichnis aufräumen
        shutil.rmtree(temp_dir, ignore_errors=True)


def compress_directory_multithreaded(input_dir, output_dir, num_threads=4, compression_level=3, 
                              log_file='compression_results_mt.log', error_log_file='compression_errors.log'):
    """
    Komprimiert alle Dateien in einem Verzeichnis mit mehreren Threads.
    
    Args:
        input_dir (str): Pfad zum Quellverzeichnis
        output_dir (str): Pfad zum Ausgabeverzeichnis
        num_threads (int, optional): Anzahl der zu verwendenden Threads
        compression_level (int, optional): Komprimierungsstufe (1-22)
        log_file (str, optional): Pfad zur Log-Datei
        error_log_file (str, optional): Pfad zur Fehler-Log-Datei
    
    Returns:
        dict: Statistik über die Komprimierung
    """
    logger.info(f"Starte multithreaded Komprimierung des Verzeichnisses: {input_dir}")
    logger.info(f"Verwende {num_threads} Threads")
    
    # Fehler-Log-Datei initialisieren
    with open(error_log_file, 'w', encoding='utf-8') as f:
        f.write(f"ARC-X Gaming Compressor - Fehlerprotokoll\n")
        f.write(f"Datum: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Quellverzeichnis: {input_dir}\n")
        f.write(f"Ausgabeverzeichnis: {output_dir}\n")
        f.write(f"Komprimierungsstufe: {compression_level}\n")
        f.write(f"Anzahl Threads: {num_threads}\n")
        f.write("-" * 100 + "\n")
        f.write(f"{'Dateipfad':<70} {'Fehler':<30}\n")
        f.write("-" * 100 + "\n")
    
    # Sicherstellen, dass das Ausgabeverzeichnis existiert
    os.makedirs(output_dir, exist_ok=True)
    
    # Statistik initialisieren
    stats = {
        'total_files': 0,
        'failed_files': 0,
        'total_original_size': 0,
        'total_compressed_size': 0,
        'categories': {
            'Textur': {'count': 0, 'original_size': 0, 'compressed_size': 0},
            'Audio': {'count': 0, 'original_size': 0, 'compressed_size': 0},
            'Modell': {'count': 0, 'original_size': 0, 'compressed_size': 0},
            'Script': {'count': 0, 'original_size': 0, 'compressed_size': 0},
            'Sonstige': {'count': 0, 'original_size': 0, 'compressed_size': 0}
        },
        'processing_time': 0
    }
    
    # Thread-sichere Locks für die Aktualisierung der Statistik und Fehlerlog
    stats_lock = threading.Lock()
    error_log_lock = threading.Lock()
    
    # Log-Datei erstellen
    with open(log_file, 'w', encoding='utf-8') as f:
        f.write("ARC-X Gaming Compressor - Multithreaded Komprimierungsergebnisse\n")
        f.write(f"Datum: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Quellverzeichnis: {input_dir}\n")
        f.write(f"Ausgabeverzeichnis: {output_dir}\n")
        f.write(f"Komprimierungsstufe: {compression_level}\n")
        f.write(f"Anzahl Threads: {num_threads}\n")
        f.write("-" * 100 + "\n")
        f.write(f"{'Dateipfad':<50} {'Kategorie':<10} {'Original':<15} {'Komprimiert':<15} {'Ratio':<10}\n")
        f.write("-" * 100 + "\n")
    
    # Funktion, die von jedem Thread ausgeführt wird
    def process_file(file_info):
        file_path, rel_path = file_info
        
        # Ausgabepfad im Zielverzeichnis erstellen
        output_path = os.path.join(output_dir, rel_path + '.zst')
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        try:
            # Kategorie bestimmen
            if is_texture(file_path):
                category = "Textur"
            elif is_audio(file_path):
                category = "Audio"
            elif is_model(file_path):
                category = "Modell"
            elif is_script(file_path):
                category = "Script"
            else:
                category = "Sonstige"
            
            # Datei komprimieren
            original_size, compressed_size, ratio = compress_file(file_path, output_path, compression_level)
            
            # Thread-sicher die Statistik aktualisieren
            with stats_lock:
                stats['total_files'] += 1
                stats['total_original_size'] += original_size
                stats['total_compressed_size'] += compressed_size
                stats['categories'][category]['count'] += 1
                stats['categories'][category]['original_size'] += original_size
                stats['categories'][category]['compressed_size'] += compressed_size
                
                # In Log-Datei schreiben
                with open(log_file, 'a', encoding='utf-8') as f:
                    f.write(f"{rel_path:<50} {category:<10} {format_size(original_size):<15} "
                            f"{format_size(compressed_size):<15} {ratio:.2f}x\n")
            
            return True, None
        
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Fehler beim Komprimieren von {file_path}: {error_msg}")
            
            # Thread-sicher in die Fehler-Log-Datei schreiben
            with error_log_lock:
                stats['failed_files'] += 1
                
                with open(error_log_file, 'a', encoding='utf-8') as f:
                    f.write(f"{rel_path:<70} {error_msg[:30]}\n")
                    
                    # Detaillierte Fehlerinformationen
                    f.write(f"  Vollständiger Fehler: {error_msg}\n")
                    f.write(f"  Stack-Trace:\n")
                    import traceback
                    for line in traceback.format_exc().splitlines():
                        f.write(f"    {line}\n")
                    f.write("-" * 100 + "\n")
            
            return False, error_msg
    
    # Liste aller zu komprimierenden Dateien erstellen
    files_to_process = []
    for root, _, files in os.walk(input_dir):
        for file in files:
            file_path = os.path.join(root, file)
            rel_path = os.path.relpath(file_path, input_dir)
            files_to_process.append((file_path, rel_path))
    
    total_files = len(files_to_process)
    logger.info(f"Insgesamt {total_files} Dateien gefunden")
    
    # Startzeit messen
    start_time = time.time()
    
    # Fortschritts-Counter (thread-sicher)
    completed_files = 0
    completed_lock = threading.Lock()
    
    # Callback-Funktion für abgeschlossene Tasks
    def task_done_callback(future):
        nonlocal completed_files
        try:
            # Ergebnis abrufen, um Ausnahmen zu erfassen
            success, error = future.result()
            
            # Thread-sicher den Fortschritt aktualisieren
            with completed_lock:
                completed_files += 1
                
                # Fortschritt anzeigen (alle 10 Dateien oder bei Abschluss)
                if completed_files % 10 == 0 or completed_files == total_files:
                    elapsed_time = time.time() - start_time
                    estimated_total = (elapsed_time / completed_files) * total_files if completed_files > 0 else 0
                    remaining_time = max(0, estimated_total - elapsed_time)
                    
                    # Zeige auch die Anzahl der fehlgeschlagenen Dateien an
                    with stats_lock:
                        failed = stats['failed_files']
                    
                    logger.info(f"Fortschritt: {completed_files}/{total_files} Dateien verarbeitet "
                               f"({completed_files / total_files * 100:.1f}%) - "
                               f"Fehler: {failed} - "
                               f"Verbleibende Zeit: ca. {remaining_time:.1f} Sekunden")
        except Exception as e:
            logger.error(f"Fehler bei der Verarbeitung einer Datei: {e}")
            # Auch in die Fehlerlog-Datei schreiben
            with error_log_lock:
                with open(error_log_file, 'a', encoding='utf-8') as f:
                    f.write(f"{'CALLBACK-FEHLER':<70} {str(e)[:30]}\n")
                    f.write(f"  Vollständiger Fehler: {str(e)}\n")
                    f.write(f"  Stack-Trace:\n")
                    import traceback
                    for line in traceback.format_exc().splitlines():
                        f.write(f"    {line}\n")
                    f.write("-" * 100 + "\n")
    
    # ThreadPoolExecutor verwenden, um die Dateien parallel zu komprimieren
    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        # Alle Dateien zur Verarbeitung einreichen und Callbacks hinzufügen
        futures = []
        for file_info in files_to_process:
            future = executor.submit(process_file, file_info)
            future.add_done_callback(task_done_callback)
            futures.append(future)
        
        # Auf Abschluss aller Tasks warten
        # concurrent.futures.wait() wartet, bis alle Futures abgeschlossen sind
        done, not_done = wait(futures)
        
        # Überprüfen, ob alle Tasks erfolgreich waren
        failed_tasks = [future for future in done if future.exception() is not None]
        if failed_tasks:
            logger.warning(f"{len(failed_tasks)} von {len(futures)} Tasks sind fehlgeschlagen.")
    
    # Endzeit messen und Gesamtzeit berechnen
    end_time = time.time()
    processing_time = end_time - start_time
    stats['processing_time'] = processing_time
    
    # Zusammenfassung in Log-Datei schreiben
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write("\n" + "-" * 100 + "\n")
        f.write("ZUSAMMENFASSUNG\n")
        f.write("-" * 100 + "\n")
        f.write(f"Gesamtanzahl Dateien: {stats['total_files']}\n")
        
        if stats['failed_files'] > 0:
            f.write(f"Fehlgeschlagene Dateien: {stats['failed_files']} (siehe {error_log_file} für Details)\n")
        
        if stats['total_compressed_size'] > 0:
            overall_ratio = stats['total_original_size'] / stats['total_compressed_size']
        else:
            overall_ratio = 0
            
        f.write(f"Gesamtgröße (Original): {format_size(stats['total_original_size'])}\n")
        f.write(f"Gesamtgröße (Komprimiert): {format_size(stats['total_compressed_size'])}\n")
        f.write(f"Gesamtersparnis: {format_size(stats['total_original_size'] - stats['total_compressed_size'])}\n")
        f.write(f"Durchschnittliche Kompressionsrate: {overall_ratio:.2f}x\n")
        f.write(f"Verarbeitungszeit: {processing_time:.2f} Sekunden\n")
        
        # Berechne die durchschnittliche Zeit pro erfolgreicher Datei
        successful_files = stats['total_files']
        if successful_files > 0:
            f.write(f"Durchschnittliche Zeit pro Datei: {processing_time / successful_files:.4f} Sekunden\n\n")
        else:
            f.write(f"Durchschnittliche Zeit pro Datei: N/A (keine erfolgreichen Dateien)\n\n")
        
        f.write("Aufschlüsselung nach Kategorien:\n")
        for category, data in stats['categories'].items():
            if data['count'] > 0:
                if data['compressed_size'] > 0:
                    cat_ratio = data['original_size'] / data['compressed_size']
                else:
                    cat_ratio = 0
                    
                f.write(f"{category}: {data['count']} Dateien, "
                        f"Original: {format_size(data['original_size'])}, "
                        f"Komprimiert: {format_size(data['compressed_size'])}, "
                        f"Ratio: {cat_ratio:.2f}x\n")
    
    logger.info(f"Multithreaded Komprimierung abgeschlossen. {stats['total_files']} Dateien in {processing_time:.2f} Sekunden komprimiert.")
    
    if stats['failed_files'] > 0:
        logger.warning(f"{stats['failed_files']} Dateien konnten nicht komprimiert werden. Details in {error_log_file}")
    
    if stats['total_files'] > 0:
        logger.info(f"Durchschnittliche Zeit pro Datei: {processing_time / stats['total_files']:.4f} Sekunden")
    
    logger.info(f"Ergebnisse wurden in {log_file} gespeichert.")
    
    return stats


def extract_arcx_archive(archive_path, output_dir, log_file='decompression_results.log'):
    """
    Extrahiert ein ARCX-Archiv in ein Verzeichnis.
    
    Args:
        archive_path (str): Pfad zum ARCX-Archiv
        output_dir (str): Pfad zum Ausgabeverzeichnis
        log_file (str, optional): Pfad zur Log-Datei
    
    Returns:
        dict: Statistik über die Dekomprimierung
    """
    logger.info(f"Starte Extraktion des ARCX-Archivs: {archive_path}")
    
    # Sicherstellen, dass das Ausgabeverzeichnis existiert
    os.makedirs(output_dir, exist_ok=True)
    
    # Temporäres Verzeichnis für die Extraktion erstellen
    import tempfile
    temp_dir = tempfile.mkdtemp(prefix="arcx_extract_temp_")
    
    try:
        # Statistik initialisieren
        stats = {
            'total_files': 0,
            'total_original_size': 0,
            'total_compressed_size': 0,
            'categories': {
                'Textur': {'count': 0, 'original_size': 0, 'compressed_size': 0},
                'Audio': {'count': 0, 'original_size': 0, 'compressed_size': 0},
                'Modell': {'count': 0, 'original_size': 0, 'compressed_size': 0},
                'Script': {'count': 0, 'original_size': 0, 'compressed_size': 0},
                'Sonstige': {'count': 0, 'original_size': 0, 'compressed_size': 0}
            }
        }
        
        # ARCX-Archiv extrahieren
        import zipfile
        with zipfile.ZipFile(archive_path, 'r') as zipf:
            # Zuerst die Metadaten extrahieren
            zipf.extract("arcx_metadata.json", temp_dir)
            
            # Metadaten laden
            import json
            with open(os.path.join(temp_dir, "arcx_metadata.json"), 'r', encoding='utf-8') as f:
                metadata = json.load(f)
            
            # Alle Dateien extrahieren
            zipf.extractall(temp_dir)
        
        # Log-Datei initialisieren
        with open(log_file, 'w', encoding='utf-8') as f:
            f.write(f"ARC-X Gaming Compressor - Dekomprimierungsergebnisse\n")
            f.write(f"Datum: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Quell-Archiv: {archive_path}\n")
            f.write(f"Ausgabeverzeichnis: {output_dir}\n")
            f.write(f"Archiv-Version: {metadata.get('version', 'Unbekannt')}\n")
            f.write("-" * 120 + "\n")
            f.write("DEKOMPRESSIONSDETAILS:\n")
            f.write("-" * 120 + "\n")
            f.write(f"{'Dateipfad':<50} {'Kategorie':<10} {'Komprimiert':<15} {'Original':<15} {'Ratio':<20}\n")
            f.write("-" * 120 + "\n")
        
        # Alle Dateien dekomprimieren
        for file_info in metadata['files']:
            file_path = file_info['path']
            category = file_info['category']
            original_size = file_info['original_size']
            compressed_size = file_info['compressed_size']
            
            # Komprimierte Datei
            compressed_path = os.path.join(temp_dir, file_path + ".zst")
            
            # Ausgabepfad
            output_path = os.path.join(output_dir, file_path)
            
            # Sicherstellen, dass das Zielverzeichnis existiert
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Datei dekomprimieren
            logger.info(f"Dekomprimiere {compressed_path}")
            import zstandard as zstd
            dctx = zstd.ZstdDecompressor()
            with open(compressed_path, 'rb') as ifh, open(output_path, 'wb') as ofh:
                dctx.copy_stream(ifh, ofh)
            
            # Statistik aktualisieren
            stats['total_files'] += 1
            stats['total_original_size'] += original_size
            stats['total_compressed_size'] += compressed_size
            
            if category in stats['categories']:
                stats['categories'][category]['count'] += 1
                stats['categories'][category]['original_size'] += original_size
                stats['categories'][category]['compressed_size'] += compressed_size
            else:
                stats['categories']['Sonstige']['count'] += 1
                stats['categories']['Sonstige']['original_size'] += original_size
                stats['categories']['Sonstige']['compressed_size'] += compressed_size
            
            # Kompressionsrate berechnen
            if compressed_size > 0:
                ratio = original_size / compressed_size
            else:
                ratio = 0
            
            # In Log-Datei schreiben
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(f"{file_path:<50} {category:<10} {format_size(compressed_size):<15} {format_size(original_size):<15} {ratio:.2f}x\n")
        
        # Zusammenfassung in Log-Datei schreiben
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write("\n" + "-" * 120 + "\n")
            f.write("ZUSAMMENFASSUNG\n")
            f.write("-" * 120 + "\n")
            
            if stats['total_compressed_size'] > 0:
                overall_ratio = stats['total_original_size'] / stats['total_compressed_size']
            else:
                overall_ratio = 0
                
            f.write(f"Gesamtanzahl Dateien: {stats['total_files']}\n")
            f.write(f"Gesamtgröße (Original): {format_size(stats['total_original_size'])}\n")
            f.write(f"Gesamtgröße (Komprimiert): {format_size(stats['total_compressed_size'])}\n")
            f.write(f"Gesamtersparnis: {format_size(stats['total_original_size'] - stats['total_compressed_size'])}\n")
            f.write(f"Durchschnittliche Kompressionsrate: {overall_ratio:.2f}x\n\n")
            
            f.write("Aufschlüsselung nach Kategorien:\n")
            for category, data in stats['categories'].items():
                if data['count'] > 0:
                    if data['compressed_size'] > 0:
                        cat_ratio = data['original_size'] / data['compressed_size']
                    else:
                        cat_ratio = 0
                        
                    f.write(f"{category}: {data['count']} Dateien, "
                            f"Original: {format_size(data['original_size'])}, "
                            f"Komprimiert: {format_size(data['compressed_size'])}, "
                            f"Ratio: {cat_ratio:.2f}x\n")
        
        logger.info(f"Extraktion abgeschlossen. {stats['total_files']} Dateien dekomprimiert.")
        logger.info(f"Ergebnisse wurden in {log_file} gespeichert.")
        
        return stats
    
    finally:
        # Temporäres Verzeichnis aufräumen
        shutil.rmtree(temp_dir, ignore_errors=True)

def main():
    """
    Hauptfunktion des Programms.
    """
    parser = argparse.ArgumentParser(description='ARC-X Gaming Compressor - Verzeichnisscanner und Komprimierer')
    parser.add_argument('directory', help='Zu durchsuchendes Verzeichnis oder ARCX-Archiv')
    parser.add_argument('--log', default='before_compression.log', help='Pfad zur Log-Datei (Standard: before_compression.log)')
    parser.add_argument('--compress', action='store_true', help='Dateien komprimieren und ARCX-Archiv erstellen')
    parser.add_argument('--decompress', action='store_true', help='ARCX-Archiv dekomprimieren')
    parser.add_argument('--multithreaded', action='store_true', help='Multithreaded Komprimierung verwenden')
    parser.add_argument('--threads', type=int, default=4, help='Anzahl der zu verwendenden Threads (Standard: 4)')
    parser.add_argument('--output', default=None, help='Name der Ausgabe-Archivdatei oder -verzeichnisses')
    parser.add_argument('--level', type=int, default=None, choices=range(1, 23), help='Komprimierungsstufe (1-22, Standard: automatisch basierend auf Dateityp)')
    parser.add_argument('--extract-dir', default=None, help='Verzeichnis für die Ausgabe der komprimierten Dateien (ohne Archiv)')
    
    args = parser.parse_args()
    
    # Absoluten Pfad für die Log-Datei erstellen
    log_path = args.log
    if not os.path.isabs(log_path):
        log_path = os.path.join(os.getcwd(), log_path)
    
    # Wenn --decompress angegeben wurde, ARCX-Archiv extrahieren
    if args.decompress:
        # Überprüfen, ob die angegebene Datei existiert und eine ARCX-Datei ist
        if not os.path.isfile(args.directory) or not args.directory.lower().endswith('.arcx'):
            logger.error(f"Die angegebene Datei ist kein gültiges ARCX-Archiv: {args.directory}")
            return
        
        # Ausgabeverzeichnis bestimmen
        if args.output is None:
            # Standardmäßig den Namen des Archivs ohne Endung verwenden
            output_dir = os.path.splitext(os.path.basename(args.directory))[0] + "_extracted"
            output_dir = os.path.join(os.path.dirname(args.directory), output_dir)
        else:
            output_dir = args.output
        
        # Sicherstellen, dass der Pfad absolut ist
        if not os.path.isabs(output_dir):
            output_dir = os.path.join(os.getcwd(), output_dir)
        
        # Dekomprimierungslog-Datei
        decompression_log = os.path.join(os.path.dirname(log_path), 'decompression_results.log')
        
        # ARCX-Archiv extrahieren
        extract_arcx_archive(args.directory, output_dir, decompression_log)
        
        return
    
    # Überprüfen, ob das angegebene Verzeichnis existiert
    if not os.path.isdir(args.directory):
        logger.error(f"Das angegebene Verzeichnis existiert nicht: {args.directory}")
        return
    
    # Verzeichnis scannen
    scan_directory(args.directory, log_path)
    
    # Wenn --extract-dir angegeben wurde, nur die Dateien komprimieren ohne Archiv zu erstellen
    if args.extract_dir:
        output_dir = args.extract_dir
        if not os.path.isabs(output_dir):
            output_dir = os.path.join(os.getcwd(), output_dir)
        
        os.makedirs(output_dir, exist_ok=True)
        
        if args.multithreaded:
            compression_log = os.path.join(os.path.dirname(log_path), 'compression_results_mt.log')
            error_log = os.path.join(os.path.dirname(log_path), 'compression_errors.log')
            compress_directory_multithreaded(args.directory, output_dir, args.threads, args.level, 
                                           compression_log, error_log)
        else:
            logger.error("Direktes Komprimieren ohne Archiv ist nur im multithreaded Modus verfügbar.")
            logger.info("Bitte verwenden Sie --multithreaded oder entfernen Sie --extract-dir.")
    
    # Wenn --compress angegeben wurde, ARCX-Archiv erstellen
    elif args.compress:
        # Standardmäßig den Namen des Quellverzeichnisses verwenden
        if args.output is None:
            output_name = os.path.basename(os.path.normpath(args.directory))
        else:
            output_name = args.output
        
        # Sicherstellen, dass die Dateiendung .arcx ist
        if not output_name.endswith('.arcx'):
            output_name += '.arcx'
        
        # Wenn der Ausgabepfad nicht absolut ist, im aktuellen Verzeichnis erstellen
        if not os.path.isabs(output_name):
            output_file = os.path.join(os.getcwd(), output_name)
        else:
            output_file = output_name
        
        logger.info(f"ARCX-Archiv wird erstellt in: {output_file}")
        
        if args.multithreaded:
            logger.info(f"Multithreaded Komprimierung mit {args.threads} Threads wird verwendet")
            # Temporäres Verzeichnis für die komprimierten Dateien erstellen
            import tempfile
            temp_dir = tempfile.mkdtemp(prefix="arcx_mt_temp_")
            
            try:
                # Dateien multithreaded komprimieren
                compression_log = os.path.join(os.path.dirname(log_path), 'compression_results_mt.log')
                error_log = os.path.join(os.path.dirname(log_path), 'compression_errors.log')
                stats = compress_directory_multithreaded(args.directory, temp_dir, args.threads, args.level, 
                                                       compression_log, error_log)
                
                # Metadaten-Datei für das Archiv erstellen
                metadata = {
                    'version': '1.0',
                    'created': datetime.now().isoformat(),
                    'compression_level': args.level,
                    'threads_used': args.threads,
                    'files': []
                }
                
                # Metadaten für jede Datei hinzufügen
                for root, _, files in os.walk(temp_dir):
                    for file in files:
                        if file.endswith('.zst'):
                            file_path = os.path.join(root, file)
                            rel_path = os.path.relpath(file_path, temp_dir)
                            # Entferne die .zst-Endung für den relativen Pfad
                            rel_path = rel_path[:-4]  # Entferne '.zst'
                            
                            # Originaldatei finden
                            original_path = os.path.join(args.directory, rel_path)
                            
                            # Kategorie bestimmen
                            if is_texture(original_path):
                                category = "Textur"
                            elif is_audio(original_path):
                                category = "Audio"
                            elif is_model(original_path):
                                category = "Modell"
                            elif is_script(original_path):
                                category = "Script"
                            else:
                                category = "Sonstige"
                            
                            # Größen ermitteln
                            original_size = os.path.getsize(original_path)
                            compressed_size = os.path.getsize(file_path)
                            
                            # Metadaten für diese Datei hinzufügen
                            metadata['files'].append({
                                'path': rel_path,
                                'category': category,
                                'original_size': original_size,
                                'compressed_size': compressed_size
                            })
                
                # Metadaten als JSON in temporäres Verzeichnis schreiben
                import json
                metadata_path = os.path.join(temp_dir, "arcx_metadata.json")
                with open(metadata_path, 'w', encoding='utf-8') as f:
                    json.dump(metadata, f, indent=2)
                
                # Alle komprimierten Dateien und Metadaten in ein ZIP-Archiv packen
                import zipfile
                with zipfile.ZipFile(output_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
                    # Zuerst die Metadaten hinzufügen
                    zipf.write(metadata_path, "arcx_metadata.json")
                    
                    # Dann alle komprimierten Dateien
                    for root, _, files in os.walk(temp_dir):
                        for file in files:
                            if file == "arcx_metadata.json":
                                continue  # Metadaten haben wir bereits hinzugefügt
                            
                            file_path = os.path.join(root, file)
                            arcname = os.path.relpath(file_path, temp_dir)
                            zipf.write(file_path, arcname)
                
                # Größe der finalen ARCX-Datei ermitteln
                arcx_size = os.path.getsize(output_file)
                logger.info(f"ARCX-Archiv erstellt: {output_file} ({format_size(arcx_size)})")
                logger.info(f"Multithreaded Komprimierung abgeschlossen. {stats['total_files']} Dateien komprimiert.")
                logger.info(f"Ergebnisse wurden in {compression_log} gespeichert.")
                
            finally:
                # Temporäres Verzeichnis aufräumen
                shutil.rmtree(temp_dir, ignore_errors=True)
        else:
            # Standardmäßige single-threaded Komprimierung
            compression_log = os.path.join(os.path.dirname(log_path), 'compression_results.log')
            create_arcx_archive(args.directory, output_file, args.level, compression_log)

if __name__ == "__main__":
    main()