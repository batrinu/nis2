"""
Romanian NIS2 Audit Assessor
Implements audit methodology specific to Romanian NIS2 transposition.
Based on OUG 155/2024 and DNSC implementation orders.
"""
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum


class AuditPhase(Enum):
    """Romanian audit phases per DNSC methodology."""
    PREGATIRE = "Pregătire și Planificare"
    CLASIFICARE = "Verificare Clasificare"
    DOCUMENTE = "Examinare Documente"
    TEHNIC = "Evaluare Tehnică"
    CONFORMITATE = "Evaluare Conformitate CyFun"
    RAPORTARE = "Raportare și Recomandări"


class ConformityLevel(Enum):
    """Conformity levels for Romanian audit."""
    CONFORM = "Conform"
    PARTIAL_CONFORM = "Parțial Conform"
    NECONFORM = "Neconform"
    CRITIC = "Critic"


@dataclass
class RomanianFinding:
    """A finding from Romanian audit."""
    cod: str
    categorie: str
    descriere: str
    nivel_risc: str  # CRITIC, MAJOR, MINOR
    referinta_legal: str
    recomandare: str
    termen_remediere: str


@dataclass
class DomainAssessment:
    """Assessment for a specific domain."""
    domeniu: str
    scor: float
    nivel_conformitate: str
    constatari: List[RomanianFinding]
    masuri_implementate: int
    masuri_necesare: int


@dataclass
class RomanianAuditResult:
    """Complete Romanian audit result."""
    # Identificare
    id_audit: str
    entitate_id: str
    nume_entitate: str
    data_audit: datetime
    auditor: str
    
    # Clasificare
    clasificare: str  # ESENTIAL / IMPORTANT / BASIC
    nivel_cyfun: str  # ESENTIAL / IMPORTANT / BASIC
    cod_sector: str
    
    # Scoruri
    scor_general: float
    scor_guvernanta: float
    scor_identificare: float
    scor_protectie: float
    scor_detectare: float
    scor_raspuns: float
    scor_recuperare: float
    
    # Evaluări domenii
    evaluari_domenii: List[DomainAssessment]
    
    # Constatari
    constatari_critice: List[RomanianFinding]
    constatari_majore: List[RomanianFinding]
    constatari_minore: List[RomanianFinding]
    
    # Conformitate
    nivel_conformitate_general: str
    conform_cyfun: bool
    plan_remediere_necesar: bool
    
    # Termene
    termen_remediere_critice: str
    termen_remediere_majore: str
    termen_remediere_minore: str
    
    # Recomandări
    recomandari_prioritare: List[str]
    actiuni_imediate: List[str]
    
    # Următoarele etape
    data_urmator_audit: str
    data_intermediara: Optional[str]
    
    # Referințe legale
    baza_legala: List[str]
    
    # Date suplimentare (opționale)
    enire_score: Optional[int] = None
    enire_cyfun_level: Optional[str] = None
    target_maturity: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id_audit": self.id_audit,
            "entitate_id": self.entitate_id,
            "nume_entitate": self.nume_entitate,
            "data_audit": self.data_audit.isoformat(),
            "auditor": self.auditor,
            "clasificare": self.clasificare,
            "nivel_cyfun": self.nivel_cyfun,
            "cod_sector": self.cod_sector,
            "scor_general": self.scor_general,
            "scoruri_categorii": {
                "GV_Guvernanta": self.scor_guvernanta,
                "ID_Identificare": self.scor_identificare,
                "PR_Protectie": self.scor_protectie,
                "DE_Detectare": self.scor_detectare,
                "RS_Raspuns": self.scor_raspuns,
                "RC_Recuperare": self.scor_recuperare,
            },
            "evaluari_domenii": [
                {
                    "domeniu": e.domeniu,
                    "scor": e.scor,
                    "nivel_conformitate": e.nivel_conformitate,
                    "masuri_implementate": e.masuri_implementate,
                    "masuri_necesare": e.masuri_necesare,
                }
                for e in self.evaluari_domenii
            ],
            "constatari": {
                "critice": len(self.constatari_critice),
                "majore": len(self.constatari_majore),
                "minore": len(self.constatari_minore),
                "detalii_critice": [
                    {"cod": c.cod, "descriere": c.descriere, "termen": c.termen_remediere}
                    for c in self.constatari_critice
                ],
            },
            "conformitate": {
                "nivel_general": self.nivel_conformitate_general,
                "conform_cyfun": self.conform_cyfun,
                "plan_remediere_necesar": self.plan_remediere_necesar,
            },
            "termene_remediere": {
                "critice": self.termen_remediere_critice,
                "majore": self.termen_remediere_majore,
                "minore": self.termen_remediere_minore,
            },
            "recomandari": self.recomandari_prioritare,
            "actiuni_imediate": self.actiuni_imediate,
            "urmatorul_audit": self.data_urmator_audit,
            "baza_legala": self.baza_legala,
        }


class RomanianAuditAssessor:
    """
    Romanian NIS2 Audit Assessor.
    
    Implements the audit methodology specific to Romanian NIS2 transposition
    with detailed output in Romanian language.
    """
    
    # Category names in Romanian
    CATEGORII_CYFUN = {
        "GV": "Guvernanță",
        "ID": "Identificare",
        "PR": "Protecție",
        "DE": "Detectare",
        "RS": "Răspuns",
        "RC": "Recuperare"
    }
    
    # Risk levels
    NIVELURI_RISC = ["CRITIC", "MAJOR", "MINOR"]
    
    def __init__(self):
        """Initialize Romanian audit assessor."""
        self.baza_legala = [
            "OUG 155/2024 - Implementarea NIS2 în România",
            "Legea 124/2025 - Aprobarea OUG 155/2024",
            "Ordinul DNSC 1/2025 - Cerințe minime de securitate",
            "Ordinul DNSC 2/2025 - Evaluare risc ENIRE",
            "CyberFundamentals Framework 2025 (CyFun)",
        ]
    
    def execute_audit(
        self,
        entity_data,
        ro_classification: Dict[str, Any],
        cyfun_result: Optional[Dict] = None,
        enire_result: Optional[Dict] = None
    ) -> RomanianAuditResult:
        """
        Execute comprehensive Romanian NIS2 audit.
        
        Args:
            entity_data: Entity input data
            ro_classification: Romanian classification result
            cyfun_result: Optional CyFun maturity assessment
            enire_result: Optional ENIRE risk assessment
            
        Returns:
            Detailed Romanian audit result
        """
        audit_id = f"AUD-RO-{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}"
        
        # Get entity info
        entity_id = entity_data.entity_id
        nume_entitate = entity_data.legal_name
        clasificare = ro_classification.get("classification", "BASIC").upper()
        nivel_cyfun = ro_classification.get("cyfun_level", "BASIC")
        cod_sector = ro_classification.get("sector_code", "N/A")
        
        # Calculate scores based on CyFun or generate simulated
        if cyfun_result:
            scoruri = self._extract_cyfun_scores(cyfun_result)
        else:
            scoruri = self._generate_simulated_scores(clasificare)
        
        # Calculate overall score
        scor_general = sum(scoruri.values()) / len(scoruri)
        
        # Create domain assessments
        evaluari_domenii = self._create_domain_assessments(scoruri, clasificare)
        
        # Generate findings based on scores
        constatari = self._generate_findings(scoruri, clasificare, cod_sector)
        
        # Determine conformity
        conform_cyfun = self._check_cyfun_compliance(clasificare, scor_general, scoruri)
        nivel_conformitate = self._determine_conformity_level(scor_general, constatari)
        
        # Remediation plan required?
        plan_remediere = not conform_cyfun or len(constatari["critice"]) > 0
        
        # Set remediation deadlines based on classification
        termene = self._calculate_remediation_deadlines(clasificare, constatari)
        
        # Generate recommendations
        recomandari = self._generate_recommendations(clasificare, constatari, scoruri)
        actiuni_imediate = self._generate_immediate_actions(constatari["critice"])
        
        # Next audit date
        data_urmator_audit = self._calculate_next_audit_date(clasificare)
        
        return RomanianAuditResult(
            id_audit=audit_id,
            entitate_id=entity_id,
            nume_entitate=nume_entitate,
            data_audit=datetime.now(timezone.utc),
            auditor="AUDITOR-DNSC-001",
            clasificare=clasificare,
            nivel_cyfun=nivel_cyfun,
            cod_sector=cod_sector,
            scor_general=round(scor_general, 2),
            scor_guvernanta=scoruri["GV"],
            scor_identificare=scoruri["ID"],
            scor_protectie=scoruri["PR"],
            scor_detectare=scoruri["DE"],
            scor_raspuns=scoruri["RS"],
            scor_recuperare=scoruri["RC"],
            evaluari_domenii=evaluari_domenii,
            constatari_critice=constatari["critice"],
            constatari_majore=constatari["majore"],
            constatari_minore=constatari["minore"],
            nivel_conformitate_general=nivel_conformitate,
            conform_cyfun=conform_cyfun,
            plan_remediere_necesar=plan_remediere,
            termen_remediere_critice=termene["critice"],
            termen_remediere_majore=termene["majore"],
            termen_remediere_minore=termene["minore"],
            recomandari_prioritare=recomandari,
            actiuni_imediate=actiuni_imediate,
            data_urmator_audit=data_urmator_audit,
            data_intermediara=None,
            baza_legala=self.baza_legala,
            enire_score=enire_result.get("risk_score") if enire_result else None,
            enire_cyfun_level=enire_result.get("cyfun_level") if enire_result else None,
            target_maturity=cyfun_result.get("target_maturity", 0) if cyfun_result else 0
        )
    
    def _extract_cyfun_scores(self, cyfun_result: Dict) -> Dict[str, float]:
        """Extract scores from CyFun result."""
        categories = cyfun_result.get("categories", {})
        
        def get_score(cat_obj, default=3.0):
            """Helper to get score from dict or dataclass."""
            if hasattr(cat_obj, 'overall_score'):
                return cat_obj.overall_score
            elif isinstance(cat_obj, dict):
                return cat_obj.get("overall_score", default)
            return default
        
        return {
            "GV": get_score(categories.get("GV", {})),
            "ID": get_score(categories.get("ID", {})),
            "PR": get_score(categories.get("PR", {})),
            "DE": get_score(categories.get("DE", {})),
            "RS": get_score(categories.get("RS", {})),
            "RC": get_score(categories.get("RC", {})),
        }
    
    def _generate_simulated_scores(self, clasificare: str) -> Dict[str, float]:
        """Generate simulated scores based on classification."""
        # Essential entities should have some gaps to demonstrate remediation
        if clasificare == "ESENTIAL":
            return {
                "GV": 3.5,
                "ID": 3.2,
                "PR": 2.8,  # Gap here
                "DE": 3.0,
                "RS": 2.9,  # Gap here
                "RC": 3.1,
            }
        elif clasificare == "IMPORTANT":
            return {
                "GV": 3.2,
                "ID": 3.0,
                "PR": 2.9,
                "DE": 2.8,
                "RS": 3.0,
                "RC": 2.9,
            }
        else:  # BASIC
            return {
                "GV": 2.5,
                "ID": 2.3,
                "PR": 2.4,
                "DE": 2.2,
                "RS": 2.3,
                "RC": 2.1,
            }
    
    def _create_domain_assessments(
        self,
        scoruri: Dict[str, float],
        clasificare: str
    ) -> List[DomainAssessment]:
        """Create domain assessments."""
        evaluari = []
        
        for cod, nume in self.CATEGORII_CYFUN.items():
            scor = scoruri[cod]
            nivel = self._score_to_conformity(scor, clasificare)
            
            # Simulate measures
            masuri_total = 16 if clasificare == "ESENTIAL" else (12 if clasificare == "IMPORTANT" else 8)
            masuri_impl = int((scor / 5.0) * masuri_total)
            
            # Generate findings for this domain
            constatari = self._generate_domain_findings(cod, scor, clasificare)
            
            evaluari.append(DomainAssessment(
                domeniu=f"{cod} - {nume}",
                scor=round(scor, 2),
                nivel_conformitate=nivel,
                constatari=constatari,
                masuri_implementate=masuri_impl,
                masuri_necesare=masuri_total
            ))
        
        return evaluari
    
    def _score_to_conformity(self, scor: float, clasificare: str) -> str:
        """Convert score to conformity level."""
        threshold = 3.5 if clasificare == "ESENTIAL" else (3.0 if clasificare == "IMPORTANT" else 2.5)
        
        if scor >= threshold + 0.5:
            return ConformityLevel.CONFORM.value
        elif scor >= threshold:
            return ConformityLevel.PARTIAL_CONFORM.value
        elif scor >= threshold - 0.5:
            return ConformityLevel.NECONFORM.value
        else:
            return ConformityLevel.CRITIC.value
    
    def _generate_findings(
        self,
        scoruri: Dict[str, float],
        clasificare: str,
        cod_sector: str
    ) -> Dict[str, List[RomanianFinding]]:
        """Generate audit findings based on scores."""
        critice = []
        majore = []
        minore = []
        
        thresholds = {
            "ESENTIAL": {"crit": 2.5, "maj": 3.0, "min": 3.5},
            "IMPORTANT": {"crit": 2.0, "maj": 2.5, "min": 3.0},
            "BASIC": {"crit": 1.5, "maj": 2.0, "min": 2.5},
        }.get(clasificare, {"crit": 2.0, "maj": 2.5, "min": 3.0})
        
        # Generate findings for low scores
        if scoruri["PR"] < thresholds["maj"]:
            critice.append(RomanianFinding(
                cod="PR-001-CR",
                categorie="PR - Protecție",
                descriere="Măsuri de protecție a rețelei și sistemelor informatice insuficient implementate. Lipsă controale de acces granulare.",
                nivel_risc="CRITIC",
                referinta_legal="Art. 7(1) din OUG 155/2024, CyFun PR.OC-01",
                recomandare="Implementarea controalelor de acces bazate pe rol (RBAC) și segmentarea rețelei. Configurarea firewall-urilor la nivel de aplicație.",
                termen_remediere="30 zile"
            ))
        
        if scoruri["RS"] < thresholds["maj"]:
            majore.append(RomanianFinding(
                cod="RS-001-MA",
                categorie="RS - Răspuns",
                descriere="Procedurile de răspuns la incidente nu sunt complet documentate și testate. Lipsă exerciții periodice.",
                nivel_risc="MAJOR",
                referinta_legal="Art. 8(1) din OUG 155/2024, CyFun RS.RP-01",
                recomandare="Elaborarea planului detaliat de răspuns la incidente. Efectuarea de exerciții de răspuns la incidente semestriale.",
                termen_remediere="60 zile"
            ))
        
        if scoruri["DE"] < thresholds["min"]:
            minore.append(RomanianFinding(
                cod="DE-001-MI",
                categorie="DE - Detectare",
                descriere="Capacitățile de monitorizare și detectare pot fi îmbunătățite. Alertele nu sunt corelate automat.",
                nivel_risc="MINOR",
                referinta_legal="Art. 7(3) din OUG 155/2024, CyFun DE.AE-01",
                recomandare="Implementarea unui sistem SIEM pentru corelarea alertelor. Configurarea regulilor de detectare a anomaliilor.",
                termen_remediere="90 zile"
            ))
        
        # Add sector-specific finding
        if cod_sector.startswith("105"):  # Healthcare
            majore.append(RomanianFinding(
                cod="SEC-HEALTH-001",
                categorie="Securitatea datelor pacienților",
                descriere="Politica de confidențialitate a datelor pacienților necesită actualizare conform standardelor NIS2.",
                nivel_risc="MAJOR",
                referinta_legal="Art. 7(4) din OUG 155/2024, GDPR Art. 32",
                recomandare="Actualizarea politicii de confidențialitate. Implementarea criptării end-to-end pentru datele pacienților.",
                termen_remediere="45 zile"
            ))
        
        return {"critice": critice, "majore": majore, "minore": minore}
    
    def _generate_domain_findings(
        self,
        cod: str,
        scor: float,
        clasificare: str
    ) -> List[RomanianFinding]:
        """Generate findings for a specific domain."""
        findings = []
        
        if scor < 3.0 and clasificare == "ESENTIAL":
            findings.append(RomanianFinding(
                cod=f"{cod}-GEN-001",
                categorie=self.CATEGORII_CYFUN[cod],
                descriere=f"Nivel de maturitate sub pragul minim în categoria {self.CATEGORII_CYFUN[cod]}.",
                nivel_risc="MAJOR" if scor < 2.5 else "MINOR",
                referinta_legal=f"CyFun {cod}.OC-01",
                recomandare=f"Dezvoltarea și implementarea controalelor suplimentare în domeniul {self.CATEGORII_CYFUN[cod]}.",
                termen_remediere="60 zile"
            ))
        
        return findings
    
    def _check_cyfun_compliance(
        self,
        clasificare: str,
        scor_general: float,
        scoruri: Dict[str, float]
    ) -> bool:
        """Check if entity is CyFun compliant."""
        if clasificare == "ESENTIAL":
            return scor_general >= 3.5 and all(s >= 3.0 for s in scoruri.values())
        elif clasificare == "IMPORTANT":
            return scor_general >= 3.0 and all(s >= 2.5 for s in scoruri.values())
        else:
            return scor_general >= 2.5
    
    def _determine_conformity_level(
        self,
        scor_general: float,
        constatari: Dict[str, List[RomanianFinding]]
    ) -> str:
        """Determine overall conformity level."""
        if len(constatari["critice"]) > 0:
            return ConformityLevel.CRITIC.value
        elif len(constatari["majore"]) > 2 or scor_general < 3.0:
            return ConformityLevel.NECONFORM.value
        elif len(constatari["majore"]) > 0 or scor_general < 3.5:
            return ConformityLevel.PARTIAL_CONFORM.value
        else:
            return ConformityLevel.CONFORM.value
    
    def _calculate_remediation_deadlines(
        self,
        clasificare: str,
        constatari: Dict[str, List[RomanianFinding]]
    ) -> Dict[str, str]:
        """Calculate remediation deadlines."""
        base_days = {"ESENTIAL": 30, "IMPORTANT": 60, "BASIC": 90}.get(clasificare, 60)
        
        return {
            "critice": f"{base_days} zile",
            "majore": f"{base_days * 2} zile",
            "minore": f"{base_days * 3} zile",
        }
    
    def _generate_recommendations(
        self,
        clasificare: str,
        constatari: Dict[str, List[RomanianFinding]],
        scoruri: Dict[str, float]
    ) -> List[str]:
        """Generate prioritized recommendations."""
        recomandari = []
        
        # Add recommendations based on lowest scores
        sorted_scores = sorted(scoruri.items(), key=lambda x: x[1])
        
        for cod, scor in sorted_scores[:3]:
            if scor < 3.5:
                recomandari.append(
                    f"[{cod}] Îmbunătățirea controalelor în domeniul {self.CATEGORII_CYFUN[cod]} "
                    f"(scor actual: {scor:.1f})"
                )
        
        # Add specific recommendations based on findings
        if constatari["critice"]:
            recomandari.insert(0, "TRATAREA IMEDIATĂ a constatărilor critice de securitate")
        
        # Add classification-specific recommendations
        if clasificare == "ESENTIAL":
            recomandari.append("Implementarea unui program de exerciții cibernetice anuale cu DNSC")
            recomandari.append("Stabilirea unui canal direct de comunicare cu CSIRT-RO")
        
        return recomandari
    
    def _generate_immediate_actions(
        self,
        constatari_critice: List[RomanianFinding]
    ) -> List[str]:
        """Generate immediate action items."""
        actiuni = []
        
        for const in constatari_critice:
            actiuni.append(f"[{const.cod}] {const.recomandare.split('.')[0]}")
        
        if not actiuni:
            actiuni.append("Continuarea monitorizării conforme a sistemelor")
            actiuni.append("Programarea următorului audit de conformitate")
        
        return actiuni
    
    def _calculate_next_audit_date(self, clasificare: str) -> str:
        """Calculate next audit date."""
        from datetime import timedelta, timezone
        
        months = 12 if clasificare == "ESENTIAL" else 18
        next_date = datetime.now(timezone.utc) + timedelta(days=30*months)
        
        return next_date.strftime("%Y-%m-%d")
    
    def generate_audit_checklist(self, clasificare: str) -> List[str]:
        """Generate pre-audit checklist in Romanian."""
        checklist = [
            "[ ] Raport de evaluare a riscurilor (ultimele 12 luni)",
            "[ ] Politica de securitate a informațiilor și politici suport",
            "[ ] Planul de răspuns la incidente și proceduri",
            "[ ] Planuri de continuitate a afacerii și recuperare în caz de dezastru",
            "[ ] Inventarul activelor",
            "[ ] Politica de control al accesului și revizuiri ale accesului utilizatorilor",
            "[ ] Rapoarte de gestionare a vulnerabilităților",
            "[ ] Rapoarte de testare a penetrării (ultimele 12 luni)",
            "[ ] Politica de criptografie/criptare",
            "[ ] Documentația privind securitatea lanțului de aprovizionare",
            "[ ] Evidențele de instruire a personalului în domeniul securității",
            "[ ] Schemele de arhitectură a rețelei",
        ]
        
        if clasificare == "ESENTIAL":
            checklist.extend([
                "[ ] Certificate de conformitate CyberFundamentals",
                "[ ] Proceduri de coordonare transfrontalieră",
                "[ ] Documentație de coordonare cu CSIRT-RO",
                "[ ] Raport de evaluare ENIRE",
                "[ ] Planul de remediere (dacă este cazul)",
            ])
        elif clasificare == "IMPORTANT":
            checklist.extend([
                "[ ] Autoevaluare CyberFundamentals",
                "[ ] Planul de îmbunătățire continuă",
            ])
        
        return checklist
