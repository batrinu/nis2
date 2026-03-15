"""
Smart Defaults System - Loop 14
Intelligent defaults based on context, history, and patterns.
"""
from typing import Optional, Callable, Dict, Any, List
from datetime import datetime, timedelta
import re


class SmartDefaultEngine:
    """Engine for generating smart default values."""
    
    def __init__(self, user_prefs: Dict = None, history: Dict = None):
        self.user_prefs = user_prefs or {}
        self.history = history or {}
        self.context: Dict[str, Any] = {}
    
    def set_context(self, context: Dict[str, Any]):
        """Set current context for smart defaults."""
        self.context.update(context)
    
    def get_default(self, field_type: str, field_name: str = "") -> Optional[str]:
        """Get smart default for a field type."""
        generators = {
            "date": self._default_date,
            "datetime": self._default_datetime,
            "year": self._default_year,
            "quarter": self._default_quarter,
            "auditor": self._default_auditor,
            "location": self._default_location,
            "network": self._default_network,
            "email": self._default_email,
            "entity_name": self._default_entity_name,
            "sector": self._default_sector,
            "session_name": self._default_session_name,
        }
        
        generator = generators.get(field_type)
        if generator:
            return generator(field_name)
        
        return None
    
    def _default_date(self, field_name: str = "") -> str:
        """Generate default date."""
        return datetime.now().strftime("%Y-%m-%d")
    
    def _default_datetime(self, field_name: str = "") -> str:
        """Generate default datetime."""
        return datetime.now().strftime("%Y-%m-%d %H:%M")
    
    def _default_year(self, field_name: str = "") -> str:
        """Generate default year."""
        return str(datetime.now().year)
    
    def _default_quarter(self, field_name: str = "") -> str:
        """Generate default quarter."""
        month = datetime.now().month
        quarter = (month - 1) // 3 + 1
        return f"Q{quarter}"
    
    def _default_auditor(self, field_name: str = "") -> str:
        """Generate default auditor name."""
        # Try user preferences first
        auditor = self.user_prefs.get("default_auditor")
        if auditor:
            return auditor
        
        # Try last used name
        auditor = self.history.get("last_auditor_name")
        if auditor:
            return auditor
        
        # Try system username
        import getpass
        try:
            return getpass.getuser()
        except Exception:
            return ""
    
    def _default_location(self, field_name: str = "") -> str:
        """Generate default location."""
        # Try user preferences
        location = self.user_prefs.get("default_location")
        if location:
            return location
        
        # Try context
        location = self.context.get("location")
        if location:
            return location
        
        return "Headquarters"
    
    def _default_network(self, field_name: str = "") -> str:
        """Generate default network range."""
        # Try user preferences
        network = self.user_prefs.get("default_network_range")
        if network:
            return network
        
        # Try context from previous sessions
        networks = self.history.get("used_networks", [])
        if networks:
            return networks[-1]  # Last used
        
        return "192.168.1.0/24"
    
    def _default_email(self, field_name: str = "") -> str:
        """Generate default email."""
        email = self.user_prefs.get("default_email")
        if email:
            return email
        
        return ""
    
    def _default_entity_name(self, field_name: str = "") -> str:
        """Generate default entity name."""
        entity = self.context.get("entity_name")
        if entity:
            return entity
        
        return ""
    
    def _default_sector(self, field_name: str = "") -> str:
        """Generate default sector."""
        sectors = self.history.get("used_sectors", [])
        if sectors:
            # Most frequent sector
            from collections import Counter
            return Counter(sectors).most_common(1)[0][0]
        
        return ""
    
    def _default_session_name(self, field_name: str = "") -> str:
        """Generate default session name."""
        entity = self.context.get("entity_name", "Audit")
        date = datetime.now().strftime("%Y-%m-%d")
        return f"{entity} - {date}"


class PatternLearner:
    """Learn patterns from user behavior."""
    
    def __init__(self):
        self.patterns: Dict[str, List] = {}
    
    def record(self, key: str, value: Any):
        """Record a value for pattern learning."""
        if key not in self.patterns:
            self.patterns[key] = []
        
        self.patterns[key].append({
            "value": value,
            "timestamp": datetime.now().isoformat(),
        })
        
        # Keep only last 100 values
        self.patterns[key] = self.patterns[key][-100:]
    
    def get_frequent(self, key: str, n: int = 3) -> List[Any]:
        """Get most frequent values for a key."""
        if key not in self.patterns:
            return []
        
        from collections import Counter
        values = [p["value"] for p in self.patterns[key]]
        return [v for v, _ in Counter(values).most_common(n)]
    
    def get_recent(self, key: str, n: int = 5) -> List[Any]:
        """Get most recent values for a key."""
        if key not in self.patterns:
            return []
        
        values = [p["value"] for p in self.patterns[key]]
        return list(dict.fromkeys(reversed(values)))[:n]  # Deduplicate, keep order


class ContextualSuggestions:
    """Provide contextual suggestions based on current state."""
    
    SUGGESTIONS = {
        "network_scan": {
            "after_entity_creation": [
                "The network field is pre-filled based on your entity's typical range",
                "Previous scans show this network uses 192.168.x.x ranges",
            ],
            "first_time": [
                "Common home network: 192.168.1.0/24",
                "Small office: 10.0.0.0/24",
                "Large office: 10.0.0.0/16",
            ],
        },
        "entity_sector": {
            "based_on_name": {
                r"(?i)bank|financial|credit": "banking",
                r"(?i)hospital|clinic|medical|health": "health",
                r"(?i)energy|power|electric": "energy",
                r"(?i)transport|logistics|shipping": "transport",
                r"(?i)water|sewage|wastewater": "water",
            },
        },
    }
    
    def __init__(self):
        self.context: Dict[str, Any] = {}
    
    def set_context(self, context: Dict[str, Any]):
        """Set current context."""
        self.context.update(context)
    
    def get_suggestions(self, field: str) -> List[str]:
        """Get suggestions for a field."""
        suggestions = []
        
        if field == "network_range":
            suggestions.extend(self.SUGGESTIONS["network_scan"]["first_time"])
        
        elif field == "sector":
            entity_name = self.context.get("entity_name", "")
            if entity_name:
                patterns = self.SUGGESTIONS["entity_sector"]["based_on_name"]
                for pattern, sector in patterns.items():
                    if re.search(pattern, entity_name):
                        suggestions.append(f"Detected sector: {sector}")
                        break
        
        return suggestions


class SmartFormFiller:
    """Intelligent form filling based on patterns."""
    
    def __init__(self, default_engine: SmartDefaultEngine):
        self.engine = default_engine
        self.pattern_learner = PatternLearner()
    
    def fill_form(self, form_fields: Dict[str, str]) -> Dict[str, str]:
        """Fill form fields with smart defaults."""
        filled = {}
        
        for field_name, field_type in form_fields.items():
            # Try smart default first
            default = self.engine.get_default(field_type, field_name)
            if default:
                filled[field_name] = default
            else:
                # Try pattern learning
                recent = self.pattern_learner.get_recent(field_name, 1)
                if recent:
                    filled[field_name] = recent[0]
        
        return filled
    
    def suggest_corrections(self, field_name: str, value: str) -> List[str]:
        """Suggest corrections for a field value."""
        suggestions = []
        
        # Check for common mistakes
        if field_name.endswith("network") or field_name.endswith("range"):
            suggestions.extend(self._suggest_network_fixes(value))
        
        elif field_name.endswith("email"):
            suggestions.extend(self._suggest_email_fixes(value))
        
        return suggestions
    
    def _suggest_network_fixes(self, value: str) -> List[str]:
        """Suggest fixes for network range."""
        suggestions = []
        
        # Missing CIDR slash
        if re.match(r'^(\d{1,3}\.){3}\d{1,3}$', value):
            suggestions.append(f"{value}/24")
        
        # Wrong slash
        if '\\' in value:
            suggestions.append(value.replace('\\', '/'))
        
        return suggestions
    
    def _suggest_email_fixes(self, value: str) -> List[str]:
        """Suggest fixes for email."""
        suggestions = []
        
        # Common typos
        typos = {
            ".con": ".com",
            ".cm": ".com",
            ".coom": ".com",
            ".gom": ".com",
            "@gmail.con": "@gmail.com",
            "@yahoo.con": "@yahoo.com",
        }
        
        for typo, fix in typos.items():
            if typo in value:
                suggestions.append(value.replace(typo, fix))
        
        return suggestions


# Utility functions

def infer_sector_from_name(entity_name: str) -> Optional[str]:
    """Infer sector from entity name patterns."""
    patterns = {
        r"(?i)bank|financial|credit|invest": "banking",
        r"(?i)hospital|clinic|medical|health|pharma": "health",
        r"(?i)energy|power|electric|utility": "energy",
        r"(?i)transport|logistics|shipping|cargo": "transport",
        r"(?i)water|sewage|wastewater|treatment": "water",
        r"(?i)digital|tech|software|cloud|data": "digital",
        r"(?i)factory|manufacturing|production|industrial": "manufacturing",
        r"(?i)food|agriculture|farm|dairy": "food",
    }
    
    for pattern, sector in patterns.items():
        if re.search(pattern, entity_name):
            return sector
    
    return None


def suggest_network_from_history(history: List[str]) -> str:
    """Suggest network based on history."""
    if not history:
        return "192.168.1.0/24"
    
    # Find most common base
    from collections import Counter
    bases = []
    
    for network in history:
        # Extract base (e.g., 192.168.1 from 192.168.1.0/24)
        match = re.match(r'(\d+\.\d+\.\d+)\.\d+', network)
        if match:
            bases.append(match.group(1))
    
    if bases:
        most_common = Counter(bases).most_common(1)[0][0]
        return f"{most_common}.0/24"
    
    return history[-1]


def get_next_session_number(existing_sessions: List[str]) -> int:
    """Get next session number from existing sessions."""
    max_num = 0
    
    for session in existing_sessions:
        # Look for numbers in session names
        numbers = re.findall(r'\d+', session)
        for num in numbers:
            max_num = max(max_num, int(num))
    
    return max_num + 1


def format_smart_default(value: str, explanation: str) -> str:
    """Format a smart default with explanation."""
    return f"{value}  [dim]({explanation})[/]"
