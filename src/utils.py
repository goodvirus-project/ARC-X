#!/usr/bin/env python3
"""
ARC-X Gaming Compressor - Hilfsfunktionen
-----------------------------------------
Dieses Modul enthält Hilfsfunktionen für die Dateierkennung und -verarbeitung.
"""

import os
import logging

# Konfiguration des Loggings
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('ARC-X-Utils')

# Definieren der Dateiendungen für verschiedene Kategorien
TEXTURE_EXTENSIONS = ['.png', '.jpg', '.jpeg', '.tga', '.bmp', '.gif', '.tif', '.tiff', '.dds', '.ktx', '.psd']
AUDIO_EXTENSIONS = ['.mp3', '.wav', '.ogg', '.flac', '.aac', '.wma', '.m4a', '.aiff']
MODEL_EXTENSIONS = ['.fbx', '.obj', '.3ds', '.blend', '.dae', '.gltf', '.glb', '.stl', '.ply']
SCRIPT_EXTENSIONS = ['.txt', '.json', '.xml', '.lua', '.py', '.js', '.cs', '.cpp', '.c', '.h']

def is_texture(file_path):
    """
    Prüft, ob eine Datei eine Textur ist.
    
    Args:
        file_path (str): Pfad zur Datei
        
    Returns:
        bool: True, wenn die Datei eine Textur ist, sonst False
    """
    extension = os.path.splitext(file_path)[1].lower()
    return extension in TEXTURE_EXTENSIONS

def is_audio(file_path):
    """
    Prüft, ob eine Datei eine Audiodatei ist.
    
    Args:
        file_path (str): Pfad zur Datei
        
    Returns:
        bool: True, wenn die Datei eine Audiodatei ist, sonst False
    """
    extension = os.path.splitext(file_path)[1].lower()
    return extension in AUDIO_EXTENSIONS

def is_model(file_path):
    """
    Prüft, ob eine Datei ein 3D-Modell ist.
    
    Args:
        file_path (str): Pfad zur Datei
        
    Returns:
        bool: True, wenn die Datei ein 3D-Modell ist, sonst False
    """
    extension = os.path.splitext(file_path)[1].lower()
    return extension in MODEL_EXTENSIONS

def is_script(file_path):
    """
    Prüft, ob eine Datei ein Script ist.
    
    Args:
        file_path (str): Pfad zur Datei
        
    Returns:
        bool: True, wenn die Datei ein Script ist, sonst False
    """
    extension = os.path.splitext(file_path)[1].lower()
    return extension in SCRIPT_EXTENSIONS

def get_file_size(file_path):
    """
    Ermittelt die Größe einer Datei in MB.
    
    Args:
        file_path (str): Pfad zur Datei
        
    Returns:
        float: Größe der Datei in MB
        
    Raises:
        FileNotFoundError: Wenn die Datei nicht existiert
        PermissionError: Wenn keine Berechtigung zum Lesen der Datei besteht
    """
    try:
        size_bytes = os.path.getsize(file_path)
        size_mb = size_bytes / (1024 * 1024)  # Umrechnung von Bytes in MB
        return size_mb
    except FileNotFoundError:
        logger.error(f"Datei nicht gefunden: {file_path}")
        raise
    except PermissionError:
        logger.error(f"Keine Berechtigung zum Lesen der Datei: {file_path}")
        raise
    except Exception as e:
        logger.error(f"Fehler beim Ermitteln der Dateigröße von {file_path}: {e}")
        raise

def get_file_category(file_path):
    """
    Bestimmt die Kategorie einer Datei.
    
    Args:
        file_path (str): Pfad zur Datei
        
    Returns:
        str: Kategorie der Datei ('Textur', 'Audio', 'Modell', 'Script', 'Sonstige')
    """
    if is_texture(file_path):
        return "Textur"
    elif is_audio(file_path):
        return "Audio"
    elif is_model(file_path):
        return "Modell"
    elif is_script(file_path):
        return "Script"
    else:
        return "Sonstige"

def format_size(size_bytes):
    """
    Formatiert eine Größe in Bytes in eine lesbare Form.
    
    Args:
        size_bytes (int): Größe in Bytes
        
    Returns:
        str: Formatierte Größe (z.B. "1.23 MB", "45.6 KB")
    """
    # Definieren der Einheiten
    units = ['B', 'KB', 'MB', 'GB', 'TB']
    
    # Berechnen der passenden Einheit
    unit_index = 0
    size = float(size_bytes)
    
    while size >= 1024 and unit_index < len(units) - 1:
        size /= 1024
        unit_index += 1
    
    # Formatieren mit 2 Nachkommastellen
    return f"{size:.2f} {units[unit_index]}"

def get_extension(file_path):
    """
    Gibt die Dateiendung einer Datei zurück.
    
    Args:
        file_path (str): Pfad zur Datei
        
    Returns:
        str: Dateiendung (z.B. ".png", ".mp3")
    """
    return os.path.splitext(file_path)[1].lower()

def is_valid_file(file_path):
    """
    Prüft, ob eine Datei existiert und lesbar ist.
    
    Args:
        file_path (str): Pfad zur Datei
        
    Returns:
        bool: True, wenn die Datei existiert und lesbar ist, sonst False
    """
    return os.path.isfile(file_path) and os.access(file_path, os.R_OK)

def get_compression_level_by_type(file_path):
    """
    Bestimmt den optimalen Zstandard-Kompressionslevel basierend auf dem Dateityp.
    
    Verschiedene Dateitypen profitieren von unterschiedlichen Kompressionsleveln:
    - Skripte: Hoher Level für beste Kompression (meist kleine Textdateien)
    - Texturen: Mittlerer Level (Balance zwischen Kompression und Geschwindigkeit)
    - Audiodateien: Niedriger Level (oft bereits komprimiert)
    - 3D-Modelle: Mittlerer bis hoher Level (strukturierte Daten)
    - Andere: Standard-Level
    
    Args:
        file_path (str): Pfad zur Datei
        
    Returns:
        int: Zstandard-Kompressionslevel (1-22)
    """
    if is_script(file_path):
        # Skripte (.txt, .json, .xml, .lua, etc.): Hoher Level für beste Kompression
        return 12
    elif is_texture(file_path):
        # Texturen (.png, .jpg, .dds, etc.): Mittlerer Level
        return 5
    elif is_audio(file_path):
        # Audiodateien (.wav, .ogg, .mp3, etc.): Niedriger Level, da oft bereits komprimiert
        return 2
    elif is_model(file_path):
        # 3D-Modelle (.fbx, .obj, .dae, etc.): Mittlerer bis hoher Level
        return 6
    else:
        # Alle anderen Dateitypen: Standard-Level
        return 3