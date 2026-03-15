"""
Retro ASCII Art for NIS2 Field Audit Tool
Inspired by 1980s Romanian university computing (MECIPT era)
"""

# Main header with Romanian academic flair
HEADER_BIG = """
╔══════════════════════════════════════════════════════════════════╗
║     ██╗  ██╗██╗███████╗██████╗     █████╗ ██╗   ██╗██████╗ ██╗████████╗    ║
║     ██║  ██║██║██╔════╝██╔══██╗   ██╔══██╗██║   ██║██╔══██╗██║╚══██╔══╝    ║
║     ███████║██║███████╗██████╔╝   ███████║██║   ██║██║  ██║██║   ██║       ║
║     ██╔══██║██║╚════██║██╔═══╝    ██╔══██║██║   ██║██║  ██║██║   ██║       ║
║     ██║  ██║██║███████║██║        ██║  ██║╚██████╔╝██████╔╝██║   ██║       ║
║     ╚═╝  ╚═╝╚═╝╚══════╝╚═╝        ╚═╝  ╚═╝ ╚═════╝ ╚═════╝ ╚═╝   ╚═╝       ║
╠══════════════════════════════════════════════════════════════════╣
║        SISTEM DE AUDIT PENTRU DIRECTIVA NIS2                    ║
║        © 2024 - Spiritul MECIPT continua...                     ║
╚══════════════════════════════════════════════════════════════════╝
"""

# Simpler header for compact spaces
HEADER_COMPACT = """
╔══════════════════════════════════════════════════════════════╗
║  ███╗   ██╗██╗███████╗██████╗     █████╗ ██╗   ██╗██████╗    ║
║  ████╗  ██║██║██╔════╝██╔══██╗   ██╔══██╗██║   ██║██╔══██╗   ║
║  ██╔██╗ ██║██║███████╗██████╔╝   ███████║██║   ██║██║  ██║   ║
║  ██║╚██╗██║██║╚════██║██╔═══╝    ██╔══██║██║   ██║██║  ██║   ║
║  ██║ ╚████║██║███████║██║        ██║  ██║╚██████╔╝██████╔╝   ║
║  ╚═╝  ╚═══╝╚═╝╚══════╝╚═╝        ╚═╝  ╚═╝ ╚═════╝ ╚═════╝    ║
║                                                              ║
║  Sistem de Audit NIS2 | Universitatea Politehnica © 1985    ║
╚══════════════════════════════════════════════════════════════╝
"""

# Minimal header
HEADER_MINIMAL = """
┌─────────────────────────────────────────────┐
│  NIS2 AUDIT SYSTEM v2.0 - Spiritul MECIPT   │
└─────────────────────────────────────────────┘
"""

# Boot sequence messages (Romanian nostalgia)
BOOT_MESSAGES = [
    "INIȚIALIZARE SISTEM DE OPERARE...",
    "VERIFICARE MEMORIE TAMPO...",
    "INCARCARE DRIVERE PERIFERICE...",
    "CONECTARE LA BAZA DE DATE LOCALA...",
    "VERIFICARE CERTIFICARE NIS2...",
    "SISTEM PREGĂTIT PENTRU OPERARE",
]

# Romanian academic status messages
STATUS_MESSAGES = {
    "loading": [
        "Se încarcă...",
        "Procesare date...",
        "Calcul în desfășurare...",
        "Așteptați...",
    ],
    "success": [
        "Operațiune finalizată cu succes",
        "Date salvate în memorie",
        "Verificare completă",
    ],
    "error": [
        "EROARE: Verificați conexiunea",
        "EROARE: Date incomplete",
        "EROARE: Sistem indisponibil",
    ],
    "scanning": [
        "Scanare rețea în desfășurare...",
        "Detectare dispozitive...",
        "Analiză topologie...",
    ],
}

# NIS2 Classification explanations in plain language
NIS2_GUIDANCE = {
    "essential_entity": """
[ENTITATE ESENȚIALĂ - EE]

Această entitate este clasificată ca ENTITATE ESENȚIALĂ conform Articolului 3 din 
Directiva NIS2. Acest lucru înseamnă:

• Faceți parte din sectoare critice (energie, transport, banking, sănătate)
• Aveți obligații stricte de securitate cibernetică
• Trebuie să raportați incidentele în 24h la autoritatea competentă
• Sancțiuni de până la 10 milioane EUR sau 2% din cifra de afaceri

RECOMMANDARE: Implementați toate măsurile din Articolul 21.
""",
    
    "important_entity": """
[ENTITATE IMPORTANTĂ - IE]

Această entitate este clasificată ca ENTITATE IMPORTANTĂ conform Articolului 3 din 
Directiva NIS2. Acest lucru înseamnă:

• Faceți parte din sectoare importante (manufactură, digital, alimentar)
• Aveți obligații de securitate cibernetică, dar mai puțin stricte
• Trebuie să raportați incidentele în 72h la autoritatea competentă
• Sancțiuni de până la 7 milioane EUR sau 1.4% din cifra de afaceri

RECOMMANDARE: Implementați măsurile esențiale din Articolul 21.
""",
    
    "non_qualifying": """
[ENTITATE NON-CALIFICANTĂ]

Această entitate NU intră sub incidența obligațiilor stricte NIS2, dar:

• Dacă sunteți în lanțul de aprovizionare al unei EE/IE, clienții pot cere 
  dovezi de conformitate
• Este recomandată implementarea voluntară a măsurilor de bază
• Puteți deveni EE/IE dacă depășiți pragurile de mărime

RECOMMANDARE: Implementați măsurile de bază pentru protecție adecvată.
""",
}

# Article 21 checklist guidance
ARTICLE_21_GUIDANCE = {
    "risk_management": {
        "title": "Art. 21(2)(a) - Managementul riscurilor",
        "explanation": "Trebuie să aveți un proces documentat de evaluare și gestionare a riscurilor de securitate cibernetică.",
        "examples_good": [
            "Document de analiză a riscurilor actualizat anual",
            "Matrice de riscuri cu proprietari și termene",
            "Comitet de securitate cu întâlniri regulate",
        ],
        "examples_bad": [
            "Nu există document de analiză a riscurilor",
            "Riscurile nu sunt revizuite periodic",
            "Nu există responsabili desemnați",
        ],
        "why_matters": "Fără managementul riscurilor, nu știți ce trebuie să protejați și în ce ordine.",
    },
    "incident_handling": {
        "title": "Art. 21(2)(h) - Gestionarea incidentelor",
        "explanation": "Trebuie să aveți proceduri pentru detectarea, raportarea și răspunsul la incidente.",
        "examples_good": [
            "Plan de răspuns la incidente documentat",
            "Echipă de răspuns desemnată cu contacte",
            "Procedură de raportare în 24h/72h la autoritate",
        ],
        "examples_bad": [
            "Nu există plan de răspuns la incidente",
            "Nu se știe cine să contacteze în caz de incident",
            "Raportarea se face ad-hoc fără procedură",
        ],
        "why_matters": "Incidentele se vor întâmpla. Fără proceduri, pagubele sunt mai mari.",
    },
    "business_continuity": {
        "title": "Art. 21(2)(i) - Continuitatea activității",
        "explanation": "Trebuie să aveți planuri de recuperare după dezastre și backup-uri testate.",
        "examples_good": [
            "Plan de recuperare după dezastre testat anual",
            "Backup-uri automate cu testare lunară",
            "Site alternativ sau cloud pentru critical systems",
        ],
        "examples_bad": [
            "Backup-uri manuale neregulate",
            "Nu s-a testat niciodată restaurarea",
            "Nu există plan de recuperare",
        ],
        "why_matters": "Fără continuitate, un singur incident vă poate închide business-ul.",
    },
}

# Helpful hints throughout the app
CONTEXTUAL_HELP = {
    "dashboard": """
Bine ați venit în Sistemul de Audit NIS2!

Acest instrument vă ajută să evaluați conformitatea cu Directiva NIS2.

PAȘII UNUI AUDIT:
1. Creați o sesiune nouă și clasificați entitatea
2. Scanați rețeaua pentru inventarierea dispozitivelor  
3. Conectați-vă la echipamente pentru colectarea dovezilor
4. Completați lista de verificare NIS2
5. Generați raportul cu constatările și remedierea

SCURTĂTURI:
• N - Sesiune nouă
• R - Reîmprospătare listă
• ↑↓ - Navigare
• Enter - Selectare
""",
    
    "entity_classification": """
CLASIFICAREA ENTITĂȚII NIS2

Directiva NIS2 împarte entitățile în:
• ENTITĂȚI ESENȚIALE (EE) - sectoare critice, obligații stricte
• ENTITĂȚI IMPORTANTE (IE) - sectoare importante, obligații moderate  
• NON-CALIFICANTE - nu intră sub incidență directă

FACTORI DE CLASIFICARE:
• Sectorul de activitate (Anexa I sau II)
• Dimensiunea (număr angajați, cifră de afaceri)
• Operarea transfrontalieră
• Alte criterii speciale (DNS, TLD, etc.)

Rezultatul clasificării determină obligațiile specifice.
""",
    
    "network_scan": """
SCANAREA REȚELEI

Acest pas inventariază dispozitivele din rețeaua dumneavoastră.

CE CAUTĂM:
• Routere și switch-uri (infrastructură de rețea)
• Firewall-uri (securitate perimetru)
• Servere (aplicații, baze de date)
• Stații de lucru și laptop-uri
• Dispozitive IoT și industriale

RECOMANDĂRI:
• Scanați câte un segment de rețea pe rând
• Notați dispozitivele necunoscute pentru investigare
• Verificați că toate dispozitivele sunt autorizate
• Documentați topologia rețelei
""",
    
    "checklist": """
LISTA DE VERIFICARE NIS2

Această listă acoperă cerințele din Articolul 21 al Directivei NIS2.

CUM RĂSPUNDEȚI:
• DA - Măsura este implementată complet
• PARȚIAL - Măsura este parțial implementată
• NU - Măsura nu este implementată
• N/A - Nu este aplicabilă pentru acest context

PENTRU FIECARE ÎNTREBARE:
• Citiți explicația pentru a înțelege cerința
• Revizuiți exemplele de implementare bună
• Verificați dacă aveți documentația necesară
• Notați orice gap-uri identificate

Scorul de conformitate se calculează automat.
""",
}

# Fun easter eggs
EASTER_EGGS = [
    "Sistem optimizat pentru perforatoare de bandă de hârtie",
    "Memorie tampon: 1024 cuvinte (ca MECIPT-1)",
    "Viteză de procesare: 50 operații/secundă (nostalgic)",
    "Conectat la unitatea de bandă magnetică",
    "Facultatea de Automatică și Calculatoare salută utilizatorul",
    "Calculatorul personal TIM-S ar fi fost mândru",
    "Nu uitați să salvați pe dischetă înainte de ieșire",
]
