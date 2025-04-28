#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Einfache Tests für den ARC-X Gaming Compressor.
"""

import sys
import unittest

# Füge das src-Verzeichnis zum Pfad hinzu
sys.path.append('../src')

class TestImports(unittest.TestCase):
    """Test, ob alle Module korrekt importiert werden können."""

    def test_import_compressor(self):
        """Test, ob das compressor-Modul importiert werden kann."""
        try:
            import compressor
            self.assertTrue(True)
        except ImportError:
            self.fail("Konnte compressor.py nicht importieren")

    def test_import_extractor(self):
        """Test, ob das extractor-Modul importiert werden kann."""
        try:
            import extractor
            self.assertTrue(True)
        except ImportError:
            self.fail("Konnte extractor.py nicht importieren")

    def test_import_utils(self):
        """Test, ob das utils-Modul importiert werden kann."""
        try:
            import utils
            self.assertTrue(True)
        except ImportError:
            self.fail("Konnte utils.py nicht importieren")

if __name__ == '__main__':
    unittest.main()