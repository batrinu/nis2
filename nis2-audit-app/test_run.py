#!/usr/bin/env python3
"""
Quick test script to verify the NIS2 Audit App works correctly.
Run this to check all components load before launching the full TUI.
"""

import sys
import os

def verify_imports():
    """Test that all modules import correctly."""
    print("🔍 Testing imports...")
    errors = []
    
    try:
        from app.textual_app import NIS2AuditApp
        print("  ✓ Main app")
    except Exception as e:
        errors.append(f"Main app: {e}")
        print(f"  ✗ Main app: {e}")
    
    try:
        from app.tui.screens.splash import SplashScreen
        from app.tui.screens.dashboard import Dashboard
        from app.tui.screens.new_session import NewSessionWizard
        from app.tui.screens.scan import ScanScreen
        from app.tui.screens.checklist import ChecklistScreen
        from app.tui.screens.findings import FindingsScreen
        from app.tui.screens.report import ReportScreen
        print("  ✓ All TUI screens")
    except Exception as e:
        errors.append(f"Screens: {e}")
        print(f"  ✗ Screens: {e}")
    
    try:
        from app.storage.db import AuditStorage
        print("  ✓ Database")
    except Exception as e:
        errors.append(f"Database: {e}")
        print(f"  ✗ Database: {e}")
    
    try:
        from app.audit.classifier import EntityClassifier
        from app.audit.checklist import get_checklist_sections
        from app.audit.scorer import ComplianceScorer
        print("  ✓ Audit logic")
    except Exception as e:
        errors.append(f"Audit: {e}")
        print(f"  ✗ Audit: {e}")
    
    return len(errors) == 0

def verify_database():
    """Test database initialization."""
    print("\n🗄️  Testing database...")
    try:
        from app.storage.db import AuditStorage
        from app.utils import get_db_path
        
        db_path = get_db_path()
        storage = AuditStorage(db_path)
        
        # Try to list sessions
        sessions = storage.list_sessions(limit=1)
        print(f"  ✓ Database ready at: {db_path}")
        print(f"  ✓ Found {len(sessions)} existing sessions")
        return True
    except Exception as e:
        print(f"  ✗ Database error: {e}")
        return False

def check_terminal_size():
    """Check terminal size."""
    print("\n📐 Checking terminal...")
    try:
        import shutil
        cols, rows = shutil.get_terminal_size()
        print(f"  Terminal size: {cols}x{rows}")
        
        if cols < 80 or rows < 24:
            print(f"  ⚠️  Warning: Terminal may be too small (recommended: 80x24+)")
            return False
        else:
            print(f"  ✓ Terminal size is good!")
            return True
    except Exception as e:
        print(f"  ⚠️  Could not detect terminal size: {e}")
        return True

def main():
    """Run all tests."""
    print("="*60)
    print("🛡️  NIS2 Field Audit Tool - Pre-Flight Check")
    print("="*60)
    
    results = []
    results.append(("Imports", verify_imports()))
    results.append(("Database", verify_database()))
    results.append(("Terminal", check_terminal_size()))
    
    print("\n" + "="*60)
    print("📊 Test Results:")
    print("="*60)
    
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {status} - {name}")
    
    all_passed = all(r[1] for r in results)
    
    print("\n" + "="*60)
    if all_passed:
        print("🎉 All checks passed! Ready to launch!")
        print("\nTo start the application, run:")
        print("  python -m app.main")
        print("\nOr:")
        print("  python -m textual run app.textual_app:NIS2AuditApp")
    else:
        print("⚠️  Some checks failed. Please review errors above.")
    print("="*60)
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
