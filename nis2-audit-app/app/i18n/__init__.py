"""
Internationalization module for NIS2 Field Audit Tool.
RomEnglish (Romanian-English mixed) localization.

Rules:
- Technical nouns: English (network, device, scan, audit, etc.)
- Verbs/Actions: Romanian (Scanează, Salvează, Conectează, etc.)
- Descriptions: Romanian
- Navigation: Romanian with English technical terms
"""

from .ro_en import TRANSLATIONS, get_text

__all__ = ["TRANSLATIONS", "get_text"]
