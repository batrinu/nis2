#!/usr/bin/env python3
"""Demo script for RomEnglish localization."""

from app.i18n import get_text as _, TRANSLATIONS

print("=== RomEnglish Localization Demo ===\n")

# Sample translations
samples = [
    ("start_scan", _("start_scan")),
    ("device", _("device")),
    ("devices", _("devices")),
    ("scan", _("scan")),
    ("network", _("network")),
    ("save", _("save")),
    ("connect", _("connect")),
    ("audit", _("audit")),
    ("ssh", _("ssh")),
    ("firewall", _("firewall")),
    ("router", _("router")),
    ("switch", _("switch")),
    ("vulnerability", _("vulnerability")),
    ("compliance", _("compliance")),
    ("report", _("report")),
    ("status", _("status")),
    ("connected", _("connected")),
    ("welcome", _("welcome")),
    ("success", _("success")),
    ("error", _("error")),
]

print("Key technical terms (English):")
print("  network, scan, device, SSH, firewall, router, switch, audit, vulnerability")
print()
print("Sample RomEnglish translations:")
for key, value in samples[:10]:
    print(f"  {key:20} → {value}")
print()
print("Pattern: Romanian verbs/actions + English technical nouns")
print('  Ex: "Începe Scan", "Device găsit", "Conectează SSH", "Salvează report"')
print()
print(f"Total translations available: {len(TRANSLATIONS)}")
print()
print("=== UI Examples ===")
print(f"  Button: '{_('start_scan')} (S)'")
print(f"  Label:  '{_('devices')} Descoperite:'")
print(f"  Status: '{_('scan_complete')}! Găsite 5 {_('devices').lower()}'")
print(f"  Menu:   '{_('network')} Scanner'")
