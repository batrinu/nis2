"""
RomEnglish (Romanian-English Mixed) Translations

Code-switching patterns used:
- Technical nouns stay in English (network, device, scan, audit, SSH, etc.)
- Verbs and actions in Romanian (Scanează, Salvează, Conectează)
- Descriptions and labels in Romanian
- Grammar follows Romanian patterns

This reflects natural bilingual Romanian-English technical discourse.
"""

from typing import Dict, Any, Optional

# Translation dictionary: English key -> RomEnglish value
TRANSLATIONS: Dict[str, str] = {
    # === Navigation & Actions ===
    "start": "Începe",
    "scan": "Scanează",
    "save": "Salvează",
    "load": "Încarcă",
    "connect": "Conectează",
    "disconnect": "Deconectează",
    "refresh": "Reîmprospătează",
    "back": "Înapoi",
    "next": "Următorul",
    "previous": "Anteriorul",
    "cancel": "Anulează",
    "delete": "Șterge",
    "edit": "Editează",
    "view": "Vizualizează",
    "close": "Închide",
    "quit": "Ieșire",
    "exit": "Ieșire",
    "help": "Ajutor",
    "settings": "Setări",
    "menu": "Meniu",
    
    # === Main Menu ===
    "main_menu": "Meniu Principal",
    "network_discovery": "Discovery Network",
    "device_inventory": "Inventar Device-uri",
    "audit_configuration": "Configurare Audit",
    "run_audit": "Rulează Audit",
    "reports": "Rapoarte",
    "system_info": "Info Sistem",
    
    # === Scan Actions ===
    "start_scan": "Începe Scan",
    "quick_scan": "Scan Rapid",
    "full_scan": "Scan Complet",
    "custom_scan": "Scan Custom",
    "stop_scan": "Oprește Scan",
    "scan_results": "Rezultate Scan",
    "scanning": "Se scanează...",
    "scan_complete": "Scan finalizat",
    "scan_failed": "Scan eșuat",
    "no_devices_found": "Niciun device găsit",
    "devices_found": "Device-uri găsite",
    
    # === Device Terms ===
    "device": "Device",
    "devices": "Device-uri",
    "host": "Host",
    "hosts": "Host-uri",
    "ip_address": "Adresă IP",
    "mac_address": "Adresă MAC",
    "hostname": "Hostname",
    "port": "Port",
    "ports": "Port-uri",
    "service": "Service",
    "services": "Service-uri",
    "protocol": "Protocol",
    "status": "Status",
    "online": "Online",
    "offline": "Offline",
    "unknown": "Necunoscut",
    
    # === Security Terms ===
    "security": "Securitate",
    "vulnerability": "Vulnerabilitate",
    "vulnerabilities": "Vulnerabilități",
    "risk": "Risc",
    "risks": "Riscuri",
    "compliance": "Conformitate",
    "policy": "Politică",
    "encryption": "Encriptare",
    "certificate": "Certificat",
    "firewall": "Firewall",
    "password": "Parolă",
    "authentication": "Autentificare",
    "authorization": "Autorizare",
    "audit": "Audit",
    "audits": "Audit-uri",
    
    # === Network Terms ===
    "network": "Network",
    "networks": "Network-uri",
    "subnet": "Subnet",
    "gateway": "Gateway",
    "router": "Router",
    "routers": "Router-e",
    "switch": "Switch",
    "switches": "Switch-uri",
    "interface": "Interfață",
    "packet": "Packet",
    "traffic": "Traffic",
    "bandwidth": "Bandwidth",
    "latency": "Latency",
    
    # === SSH Terms ===
    "ssh": "SSH",
    "ssh_connection": "Conexiune SSH",
    "ssh_key": "SSH Key",
    "private_key": "Private Key",
    "public_key": "Public Key",
    "key_fingerprint": "Key Fingerprint",
    "remote_command": "Comandă Remote",
    
    # === Configuration ===
    "configuration": "Configurație",
    "configurations": "Configurații",
    "setting": "Setare",
    "timeout": "Timeout",
    "retry": "Reîncercare",
    "threads": "Thread-uri",
    "verbose": "Verbose",
    "debug": "Debug",
    
    # === File Operations ===
    "file": "Fișier",
    "folder": "Folder",
    "directory": "Director",
    "path": "Path",
    "export": "Exportă",
    "import": "Importă",
    "backup": "Backup",
    "restore": "Restaurează",
    
    # === Time & Progress ===
    "time": "Timp",
    "date": "Dată",
    "duration": "Durată",
    "started": "Început",
    "finished": "Finalizat",
    "in_progress": "În desfășurare",
    "pending": "În așteptare",
    "waiting": "Se așteaptă",
    "loading": "Se încarcă...",
    "processing": "Se procesează...",
    
    # === Messages ===
    "success": "Succes",
    "error": "Eroare",
    "warning": "Avertisment",
    "info": "Informație",
    "confirm": "Confirmă",
    "are_you_sure": "Ești sigur?",
    "operation_complete": "Operațiune completă",
    "operation_failed": "Operațiune eșuată",
    "please_wait": "Te rog așteaptă...",
    "not_available": "Nu este disponibil",
    "coming_soon": "În curând",
    
    # === Form Labels ===
    "name": "Nume",
    "description": "Descriere",
    "type": "Tip",
    "category": "Categorie",
    "value": "Valoare",
    "default": "Default",
    "required": "Obligatoriu",
    "optional": "Opțional",
    
    # === CLI Specific ===
    "welcome": "Bine ai venit",
    "goodbye": "La revedere",
    "select_option": "Selectează opțiunea",
    "enter_command": "Introdu comandă",
    "invalid_option": "Opțiune invalidă",
    "invalid_input": "Input invalid",
    "try_again": "Încearcă din nou",
    "press_enter": "Apasă ENTER",
    "press_any_key": "Apasă orice tastă",
    
    # === Report Terms ===
    "report": "Raport",
    "reports": "Rapoarte",
    "summary": "Rezumat",
    "details": "Detalii",
    "statistics": "Statistici",
    "findings": "Constatări",
    "recommendations": "Recomandări",
    "severity": "Severitate",
    "critical": "Critic",
    "high": "Ridicat",
    "medium": "Mediu",
    "low": "Scăzut",
    
    # === OSINT Terms ===
    "osint": "OSINT",
    "reconnaissance": "Reconnaissance",
    "whois": "WHOIS",
    "dns": "DNS",
    "domain": "Domeniu",
    "subdomain": "Subdomeniu",
    
    # === Connection Status ===
    "connected": "Conectat",
    "disconnected": "Deconectat",
    "connecting": "Se conectează...",
    "connection": "Conexiune",
    "connection_error": "Eroare Conexiune",
    "connection_timeout": "Timeout Conexiune",
    "connection_refused": "Conexiune Refuzată",
    
    # === System Info ===
    "system": "Sistem",
    "version": "Versiune",
    "platform": "Platformă",
    "memory": "Memorie",
    "cpu": "CPU",
    "disk": "Disk",
    "uptime": "Uptime",
    
    # === NIS2 Specific ===
    "nis2_compliance": "Conformitate NIS2",
    "asset_inventory": "Inventar Asset-uri",
    "risk_assessment": "Risk Assessment",
    "incident_response": "Incident Response",
    "business_continuity": "Business Continuity",
    "supply_chain": "Supply Chain",
    "cryptography": "Criptografie",
    "access_control": "Access Control",
    "multi_factor_auth": "Multi-Factor Authentication",
    
    # === Dashboard & Navigation ===
    "new_audit_session": "Audit Session Nou",
    "quick_actions": "Acțiuni Rapide",
    "statistics": "Statistici",
    "recent_audit_sessions": "Audit Sessions Recente",
    "no_audit_sessions_yet": "Niciun Audit Session Încă",
    "please_select_session_first": "Selectează un session mai întâi",
    "sessions_refreshed": "Sessions reîmprospătate",
    "audit_nou": "Audit Nou",
    "classification": "Clasificare",
    "entity": "Entitate",
    "sector": "Sector",
    "created": "Creat",
    "gata": "Gata",
    "selecteaza": "Selectează",
    
    # === Device & Connection ===
    "device_connection_manager": "Device Connection Manager",
    "ssh_credentials": "SSH Credentials",
    "device_details": "Detalii Device",
    "username": "Utilizator",
    "credentials": "Credențiale",
    "vendor": "Vendor",
    "select": "Selectează",
    "select_all": "Selectează Tot",
    "clear_selection": "Șterge Selecția",
    "connect_selected": "Conectează Selecția",
    "no_devices_selected": "Niciun device selectat",
    "loading_devices": "Se încarcă device-urile",
    "n_devices_selected": "{n} device-uri selectate",
    "device_list_refreshed": "Listă device-uri reîmprospătată",
    "running_assessment_on_n_devices": "Rulează assessment pe {n} device-uri",
    "scan_the_network_first": "Scanează network-ul mai întâi",
    "no_devices_found_for_session": "Niciun device găsit pentru acest session",
    "auto_detect": "Auto-detectare",
    "generic_ssh": "SSH Generic",
    "connecting_to": "Se conectează la {ip}",
    "connected_to_n_devices": "Conectat la {n} device-uri",
    "username_and_password_required": "Utilizator și parolă obligatorii",
    "no_connected_devices": "Niciun device conectat",
    
    # === Checklist & Compliance ===
    "nis2_compliance_assessment": "NIS2 Conformitate Assessment",
    "sections": "Secțiuni",
    "compliance_score": "Scor Conformitate",
    "question": "Întrebarea",
    "section": "Secțiune",
    "overall_progress": "Progres general",
    "article": "Articolul",
    "domain": "Domeniu",
    "yes_fully_implemented": "Da - Fully implemented",
    "partial_partially_implemented": "Parțial - Partially implemented",
    "no_not_implemented": "Nu - Not implemented",
    "previous": "Precedentul",
    "skip": "Sari peste",
    "finish": "Finalizează",
    "auto_save_ready": "Auto-save gata",
    "progress_saved": "Progres salvat",
    "nothing_to_save": "Nimic de salvat",
    "question_skipped": "Întrebare sărită",
    "youve_reached_the_end": "Ai ajuns la final",
    "da": "Da",
    "nu": "Nu",
    "partial": "Parțial",
    "sar_peste": "Sari peste",
    
    # === Findings ===
    "audit_findings": "Constatări Audit",
    "critic": "Critic",
    "ridicat": "Ridicat",
    "mediu": "Mediu",
    "scazut": "Scăzut",
    "rezolvate": "Rezolvate",
    "constatare": "Constatare",
    "constatari": "Constatări",
    "critice": "Critice",
    "ridicate": "Ridicate",
    "doar_critice": "Doar Critice",
    "doar_ridicate": "Doar Ridicate",
    "arata_toate": "Arată Toate",
    "filtreaza": "Filtrează",
    "loading_findings": "Se încarcă constatările",
    "cum_sa_repari": "Cum să Repari",
    "marcheaza_rezolvat": "Marchează Rezolvat",
    "finding_resolved": "Constatare rezolvată",
    "findings_refreshed": "Constatări reîmprospătate",
    "network_more_secure": "Network-ul tău este mai securizat",
    
    # === Report ===
    "report_generator": "Report Generator",
    "options": "Opțiuni",
    "format": "Format",
    "template": "Template",
    "output_path": "Cale Output",
    "include_sections": "Include Secțiuni",
    "standard": "Standard",
    "executive_summary": "Executive Summary",
    "technical_detail": "Technical Detail",
    "ready_to_generate_report": "Gata de generat report",
    "generate_report": "Generează Report",
    "open_folder": "Deschide Folder",
    "recent_exports": "Exporturi Recente",
    "no_recent_exports": "Niciun export recent",
    "preview": "Preview",
    "gathering_session_data": "Se colectează datele session-ului",
    "analyzing_compliance_findings": "Se analizează constatările de conformitate",
    "calculating_scores": "Se calculează scorurile",
    "formatting_report": "Se formatează report-ul",
    "writing_to_file": "Se scrie în fișier",
    "please_specify_output_path": "Specifică calea de output",
    "failed_to_save_report": "Eșuat să salveze report-ul",
    "report_saved": "Report salvat",
    "report_generated_successfully": "Report generat cu succes",
    
    # === Onboarding & Tutorial ===
    "tutorial": "Tutorial",
    "skip_tutorial": "Sari peste Tutorial",
    "get_started": "Începe",
    "continue": "Continuă",
    "felicitari": "Felicitări",
    "tutorial_complet": "Tutorial Complet",
    "bravo": "Bravo",
    "perfect": "Perfect",
    "practice_navigation": "Exersează: Navigarea",
    "practice_selecting": "Exersează: Selectarea",
    "practice_getting_help": "Exersează: Cum ceri Ajutor",
    "press_down_arrow": "Apasă tasta săgeată jos",
    "press_enter_or_space": "Apasă Enter sau Space",
    "choose_your_theme": "Alege Tema",
    "accessibility_options": "Opțiuni de Accesibilitate",
    "quick_tips": "Sfaturi Rapide",
    
    # === Keyboard Shortcuts ===
    "keyboard_shortcuts": "Scurtături Tastatură",
    "current": "Curent",
    "navigation": "Navigare",
    "actions": "Acțiuni",
    "got_it": "Am înțeles",
    "press_to_close": "Apasă pentru a închide",
    "move_between_fields": "Mută între câmpuri",
    "navigate_lists": "Navighează liste",
    "select_or_confirm": "Selectează sau confirmă",
    "show_help_for_screen": "Arată ajutor pentru screen-ul curent",
    "save_current_work": "Salvează munca curentă",
    "new_audit": "Audit nou",
    "scan_network": "Scanează network",
    "mark_as_yes_compliant": "Marchează ca Da/Compliant",
    
    # === Help System ===
    "ajutor": "Ajutor",
    "dashboard_help": "Ajutor Dashboard",
    "new_session_help": "Ajutor Sesiune Nouă",
    "network_scan_help": "Ajutor Scanare Network",
    "compliance_checklist_help": "Ajutor Checklist Conformitate",
    "findings_help": "Ajutor Constatări",
    "report_generation_help": "Ajutor Generare Report",
    "search_help": "Caută ajutor",
    "cauta": "Caută",
    "full_glossary": "Glosar Complet",
    "nis2_glossary": "Glosar NIS2",
    "glosar": "Glosar",
    
    # === Notifications & Status ===
    "centru_de_notificari": "Centru de Notificări",
    "sterge_tot": "Șterge Tot",
    "timp_necunoscut": "Timp necunoscut",
    "inca_nu_exista_notificari": "Încă nu există notificări",
    "info": "Info",
    "avertisment": "Avertisment",
    
    # === Form & Validation ===
    "this_field_is_required": "Acest câmp este obligatoriu",
    "looks_good": "✓ Arată bine",
    "unsaved_changes": "● Modificări nesalvate",
    "saved_at": "✓ Salvat la {time}",
    "saving": "⏳ Se salvează...",
    "save_failed_retrying": "⚠ Salvare eșuată - se reîncearcă",
    "field_required": "'{field}' este obligatoriu",
    "valid_format": "Format valid",
    "use_format": "Folosește formatul: 192.168.1.0/24",
    "confirm_action": "Confirmă Acțiunea",
    "yes_proceed": "Da, Continuă",
    "no_cancel": "Nu, Anulează",
    "confirm_delete": "Confirmă Ștergerea",
    "are_you_sure_delete": "Ești sigur că vrei să ștergi '{item}'?",
    "did_you_mean": "💡 Ai vrut să spui: '{suggestion}'?",
    
    # === Empty States ===
    "no_sessions": "Niciun session de audit găsit încă",
    "no_devices_discovered": "Niciun device descoperit",
    "run_scan_to_find": "Rulează un scan să găsești device-uri",
    "no_findings_yet": "Nicio constatare încă",
    "complete_checklist": "Completează checklist-ul să vezi rezultatele",
    "no_reports_generated": "Niciun report generat",
    "complete_audit_to_generate": "Completează un audit să generezi report-uri",
    "no_results_found": "Niciun rezultat găsit pentru căutarea ta",
    "try_different_terms": "Încearcă alți termeni",
    "network_not_scanned": "Network-ul nu e scanat",
    "enter_range_and_start": "Introdu un range și apasă Start Scan",
    "everything_up_to_date": "Totul e la zi",
    "answered_all_questions": "Ai răspuns la toate întrebările",
    "first_time_welcome": "Bine ai venit! Hai să setăm primul tău audit NIS2",
    
    # === Misc ===
    "ready": "Gata",
    "working": "Se lucrează...",
    "cancelling": "Se anulează...",
    "operation_took": "Operațiunea '{name}' a durat {duration:.3f}s",
    "why_am_i_seeing_this": "De ce văd asta?",
}


def get_text(key: str, default: Optional[str] = None, **kwargs) -> str:
    """
    Get translated text for a given key.
    
    Args:
        key: The translation key (English)
        default: Default value if key not found
        **kwargs: Format arguments for the translation string
        
    Returns:
        The translated RomEnglish string
        
    Examples:
        >>> get_text("start_scan")
        'Începe Scan'
        >>> get_text("devices_found", count=5)
        '5 Device-uri găsite'
    """
    text = TRANSLATIONS.get(key, default or key)
    
    if kwargs:
        try:
            text = text.format(**kwargs)
        except (KeyError, ValueError):
            # If formatting fails, return the unformatted text
            pass
    
    return text


# Convenience alias for shorter code
_ = get_text
