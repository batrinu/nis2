"""
Test User Experience Passes 122-142

Tests for user-friendly features including:
- Accessibility themes and screen reader support
- Help system and onboarding
- Progress tracking and notifications
- Undo/redo and auto-save
- Search/filter and keyboard navigation
- Backup/restore and error recovery
- Configuration wizard and user feedback
"""

import pytest
import os
import sys
import json
import tempfile
from unittest.mock import Mock, patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'nis2-audit-app', 'app'))

from user_experience import (
    UserPreferences,
    PreferenceManager,
    ThemeMode,
    ThemeEngine,
    HelpSystem,
    ProgressTracker,
    ConfirmationDialog,
    UndoManager,
    AutoSaveManager,
    SearchFilter,
    KeyboardNavigation,
    NotificationManager,
    OnboardingWizard,
    ValidationFeedback,
    AuditTrailVisualizer,
    ExportPreview,
    BatchOperationManager,
    BackupManager,
    ErrorRecovery,
    ScreenReaderSupport,
    ConfigurationWizard,
    QuickActions,
    FeedbackCollector,
)


# =============================================================================
# Pass 122: User Preference Management Tests
# =============================================================================

class TestPreferenceManager:
    """Test user preference management."""
    
    def test_preferences_defaults(self):
        """Test default preferences."""
        prefs = UserPreferences()
        assert prefs.theme == ThemeMode.DEFAULT.value
        assert prefs.auto_save is True
        assert prefs.confirm_destructive_actions is True
        assert prefs.show_help_tips is True
    
    def test_preferences_to_dict(self):
        """Test preferences serialization."""
        prefs = UserPreferences(theme='dark', font_size='large')
        data = prefs.to_dict()
        assert data['theme'] == 'dark'
        assert data['font_size'] == 'large'
    
    def test_preferences_from_dict(self):
        """Test preferences deserialization."""
        data = {'theme': 'light', 'font_size': 'small', 'auto_save': False}
        prefs = UserPreferences.from_dict(data)
        assert prefs.theme == 'light'
        assert prefs.font_size == 'small'
        assert prefs.auto_save is False
    
    def test_preference_manager_load_save(self, tmp_path):
        """Test preference manager load/save."""
        config_dir = str(tmp_path)
        manager = PreferenceManager(config_dir)
        
        # Update and save
        manager.update(theme='high_contrast', font_size='large')
        
        # Create new manager to test load
        manager2 = PreferenceManager(config_dir)
        assert manager2.get().theme == 'high_contrast'
        assert manager2.get().font_size == 'large'
    
    def test_preference_manager_reset(self, tmp_path):
        """Test preference reset to defaults."""
        config_dir = str(tmp_path)
        manager = PreferenceManager(config_dir)
        manager.update(theme='monochrome')
        
        manager.reset_to_defaults()
        assert manager.get().theme == ThemeMode.DEFAULT.value


# =============================================================================
# Pass 123: Accessibility Theme Engine Tests
# =============================================================================

class TestThemeEngine:
    """Test accessibility theme engine."""
    
    def test_get_default_theme(self):
        """Test getting default theme."""
        theme = ThemeEngine.get_theme(ThemeMode.DEFAULT)
        assert 'primary' in theme
        assert 'success' in theme
        assert 'error' in theme
    
    def test_get_high_contrast_theme(self):
        """Test high contrast theme."""
        theme = ThemeEngine.get_theme(ThemeMode.HIGH_CONTRAST)
        assert theme['background'] == '#000000'
        assert theme['text'] == '#FFFFFF'
    
    def test_get_colorblind_theme(self):
        """Test colorblind-friendly theme."""
        theme = ThemeEngine.get_theme(ThemeMode.COLORBLIND_DEUTERANOPIA)
        assert 'primary' in theme
        assert 'success' in theme
    
    def test_get_symbol_default(self):
        """Test symbol for default theme."""
        symbol = ThemeEngine.get_symbol('success', ThemeMode.DEFAULT)
        assert symbol == '✓'
    
    def test_get_symbol_high_contrast(self):
        """Test accessible symbol for high contrast."""
        symbol = ThemeEngine.get_symbol('success', ThemeMode.HIGH_CONTRAST)
        assert symbol == '[OK]'  # Text-based, not just color
    
    def test_get_symbol_error(self):
        """Test error symbol accessibility."""
        symbol = ThemeEngine.get_symbol('error', ThemeMode.MONOCHROME)
        assert '[ERR]' in symbol


# =============================================================================
# Pass 124: Contextual Help System Tests
# =============================================================================

class TestHelpSystem:
    """Test contextual help system."""
    
    def test_set_and_get_context(self):
        """Test setting and getting help context."""
        help_sys = HelpSystem()
        help_sys.set_context('device_scan')
        
        help_data = help_sys.get_help()
        assert help_data['title'] == 'Device Scan'
        assert 'scan' in help_data['description'].lower()
    
    def test_get_help_shortcuts(self):
        """Test help includes shortcuts."""
        help_sys = HelpSystem()
        help_data = help_sys.get_help('main_menu')
        
        assert 'shortcuts' in help_data
        assert len(help_data['shortcuts']) > 0
    
    def test_get_help_tips(self):
        """Test help includes tips."""
        help_sys = HelpSystem()
        help_data = help_sys.get_help('device_scan')
        
        assert 'tips' in help_data
        assert len(help_data['tips']) > 0
    
    def test_format_help_panel(self):
        """Test help panel formatting."""
        help_sys = HelpSystem()
        panel = help_sys.format_help_panel('main_menu')
        
        assert 'Main Menu' in panel
        assert 'Keyboard Shortcuts' in panel


# =============================================================================
# Pass 125: Progress Feedback System Tests
# =============================================================================

class TestProgressTracker:
    """Test progress tracking."""
    
    def test_progress_initial(self):
        """Test initial progress state."""
        tracker = ProgressTracker(10, "Test Operation")
        assert tracker.total_steps == 10
        assert tracker.current_step == 0
    
    def test_progress_update(self):
        """Test progress update."""
        tracker = ProgressTracker(10, "Test")
        result = tracker.update(5)
        
        assert result['percentage'] == 50
        assert 'visual' in result
        assert 'screen_reader' in result
    
    def test_progress_screen_reader_format(self):
        """Test screen reader friendly progress."""
        tracker = ProgressTracker(10, "Audit")
        result = tracker.update(3, "Scanning devices")
        
        assert "30%" in result['screen_reader']
        assert "step 3 of 10" in result['screen_reader']
        assert "Scanning devices" in result['screen_reader']
    
    def test_progress_complete(self):
        """Test progress completion detection."""
        tracker = ProgressTracker(5, "Test")
        tracker.update(5)
        assert tracker.is_complete() is True
    
    def test_progress_cancel(self):
        """Test progress cancellation."""
        tracker = ProgressTracker(10, "Test")
        tracker.cancel()
        assert tracker.is_cancelled() is True


# =============================================================================
# Pass 126: Confirmation Dialog System Tests
# =============================================================================

class TestConfirmationDialog:
    """Test confirmation dialogs."""
    
    def test_delete_dialog_format(self):
        """Test delete confirmation dialog."""
        dialog = ConfirmationDialog.format_dialog('delete', item='device-123')
        
        assert 'Confirm Deletion' in dialog['title']
        assert 'device-123' in dialog['message']
        assert dialog['severity'] == 'high'
    
    def test_overwrite_dialog_format(self):
        """Test overwrite confirmation dialog."""
        dialog = ConfirmationDialog.format_dialog('overwrite', item='report.pdf')
        
        assert 'Confirm Overwrite' in dialog['title']
        assert 'report.pdf' in dialog['message']
    
    def test_exit_unsaved_dialog(self):
        """Test exit unsaved changes dialog."""
        dialog = ConfirmationDialog.format_dialog('exit_unsaved')
        
        assert 'Unsaved Changes' in dialog['title']
        assert 'Save & Exit' in dialog['confirm']
        assert 'Exit Without Saving' in dialog['cancel']
    
    def test_bulk_action_dialog(self):
        """Test bulk action confirmation."""
        dialog = ConfirmationDialog.format_dialog('bulk_action', count=50)
        
        assert '50 items' in dialog['message']
        assert dialog['severity'] == 'high'


# =============================================================================
# Pass 127: Undo/Redo System Tests
# =============================================================================

class TestUndoManager:
    """Test undo/redo functionality."""
    
    def test_record_action(self):
        """Test recording actions."""
        manager = UndoManager()
        undo_fn = Mock()
        redo_fn = Mock()
        
        manager.record_action('delete', undo_fn, redo_fn, {'id': 1})
        assert manager.can_undo() is True
    
    def test_undo_execution(self):
        """Test undo execution."""
        manager = UndoManager()
        undo_fn = Mock()
        redo_fn = Mock()
        
        manager.record_action('test', undo_fn, redo_fn, {'data': 'value'})
        result = manager.undo()
        
        assert 'Undone' in result
        undo_fn.assert_called_once()
        assert manager.can_redo() is True
    
    def test_redo_execution(self):
        """Test redo execution."""
        manager = UndoManager()
        undo_fn = Mock()
        redo_fn = Mock()
        
        manager.record_action('test', undo_fn, redo_fn)
        manager.undo()
        result = manager.redo()
        
        assert 'Redone' in result
        redo_fn.assert_called_once()
    
    def test_history_limit(self):
        """Test history size limit."""
        manager = UndoManager(max_history=5)
        
        for i in range(10):
            manager.record_action(f'action_{i}', Mock(), Mock())
        
        # History should be limited to 5
        history = manager.get_history_summary()
        assert len(history) == 5


# =============================================================================
# Pass 128: Auto-Save Functionality Tests
# =============================================================================

class TestAutoSaveManager:
    """Test auto-save functionality."""
    
    def test_mark_dirty(self):
        """Test marking data as dirty."""
        save_callback = Mock()
        manager = AutoSaveManager(save_callback)
        
        manager.mark_dirty()
        assert manager.get_status()['dirty'] is True
    
    def test_save_now(self):
        """Test immediate save."""
        save_callback = Mock()
        manager = AutoSaveManager(save_callback)
        
        manager.mark_dirty()
        result = manager.save_now()
        
        assert 'Auto-saved' in result
        save_callback.assert_called_once()
        assert manager.get_status()['dirty'] is False
    
    def test_auto_save_disabled(self):
        """Test disabled auto-save."""
        save_callback = Mock()
        manager = AutoSaveManager(save_callback)
        manager.set_enabled(False)
        
        manager.mark_dirty()
        result = manager.check_and_save()
        
        assert result is None
        save_callback.assert_not_called()


# =============================================================================
# Pass 129: Search and Filter System Tests
# =============================================================================

class TestSearchFilter:
    """Test search and filter functionality."""
    
    def test_search_basic(self):
        """Test basic search."""
        sf = SearchFilter()
        items = [
            {'name': 'Device A', 'ip': '192.168.1.1'},
            {'name': 'Device B', 'ip': '192.168.1.2'},
        ]
        
        results = sf.search('Device A', items, ['name'])
        assert len(results) == 1
        assert results[0]['name'] == 'Device A'
    
    def test_search_empty_query(self):
        """Test empty search returns all items."""
        sf = SearchFilter()
        items = [{'name': 'A'}, {'name': 'B'}]
        
        results = sf.search('', items)
        assert len(results) == 2
    
    def test_apply_filters(self):
        """Test filter application."""
        sf = SearchFilter()
        items = [
            {'name': 'A', 'type': 'router'},
            {'name': 'B', 'type': 'switch'},
        ]
        
        sf.set_filter('type', 'router')
        results = sf.apply_filters(items)
        
        assert len(results) == 1
        assert results[0]['name'] == 'A'
    
    def test_format_results_summary(self):
        """Test results summary formatting."""
        sf = SearchFilter()
        sf.set_filter('type', 'router')
        
        summary = sf.format_results_summary(100, 25)
        assert 'Showing 25 of 100' in summary
        assert 'type=router' in summary


# =============================================================================
# Pass 130: Keyboard Navigation Helper Tests
# =============================================================================

class TestKeyboardNavigation:
    """Test keyboard navigation."""
    
    def test_default_mode(self):
        """Test default keyboard mode."""
        nav = KeyboardNavigation('default')
        assert nav.get_shortcut('up') == 'up'
        assert nav.get_shortcut('select') == 'enter'
    
    def test_vim_mode(self):
        """Test vim keyboard mode."""
        nav = KeyboardNavigation('vim')
        assert nav.get_shortcut('up') == 'k'
        assert nav.get_shortcut('down') == 'j'
        assert nav.get_shortcut('left') == 'h'
        assert nav.get_shortcut('right') == 'l'
    
    def test_mode_switch(self):
        """Test switching keyboard modes."""
        nav = KeyboardNavigation('default')
        nav.set_mode('vim')
        assert nav.get_shortcut('up') == 'k'
    
    def test_format_help(self):
        """Test keyboard help formatting."""
        nav = KeyboardNavigation('default')
        help_text = nav.format_help()
        
        assert 'Keyboard Shortcuts' in help_text
        assert 'up' in help_text
        assert 'down' in help_text


# =============================================================================
# Pass 131: Notification System Tests
# =============================================================================

class TestNotificationManager:
    """Test notification system."""
    
    def test_add_notification(self):
        """Test adding notification."""
        mgr = NotificationManager()
        mgr.notify('Test message', 'info')
        
        notifications = mgr.get_notifications()
        assert len(notifications) == 1
        assert notifications[0]['message'] == 'Test message'
    
    def test_filter_by_level(self):
        """Test filtering notifications by level."""
        mgr = NotificationManager()
        mgr.notify('Info message', 'info')
        mgr.notify('Error message', 'error')
        
        errors = mgr.get_notifications('error')
        assert len(errors) == 1
        assert errors[0]['message'] == 'Error message'
    
    def test_format_notification(self):
        """Test notification formatting with symbols."""
        mgr = NotificationManager()
        mgr.notify('Success!', 'success')
        
        notification = mgr.get_notifications()[0]
        formatted = mgr.format_notification(notification, ThemeMode.DEFAULT)
        
        assert 'Success!' in formatted
        assert '✓' in formatted  # Success symbol
    
    def test_dismiss_notification(self):
        """Test dismissing notification."""
        mgr = NotificationManager()
        mgr.notify('Test', 'info')
        
        mgr.dismiss(0)
        assert len(mgr.get_notifications()) == 0


# =============================================================================
# Pass 132: User Onboarding Wizard Tests
# =============================================================================

class TestOnboardingWizard:
    """Test onboarding wizard."""
    
    def test_wizard_initial_step(self):
        """Test wizard starts at first step."""
        wizard = OnboardingWizard()
        step = wizard.get_current_step()
        
        assert step['step_number'] == 1
        assert step['is_first'] is True
        assert step['is_last'] is False
    
    def test_wizard_next_step(self):
        """Test advancing to next step."""
        wizard = OnboardingWizard()
        wizard.next_step()
        
        step = wizard.get_current_step()
        assert step['step_number'] == 2
    
    def test_wizard_previous_step(self):
        """Test going back to previous step."""
        wizard = OnboardingWizard()
        wizard.next_step()
        wizard.previous_step()
        
        step = wizard.get_current_step()
        assert step['step_number'] == 1
    
    def test_wizard_completion(self):
        """Test wizard completion."""
        wizard = OnboardingWizard()
        
        # Advance through all steps
        while wizard.next_step():
            pass
        
        assert wizard.is_completed() is True
    
    def test_format_step(self):
        """Test step formatting."""
        wizard = OnboardingWizard()
        step = wizard.get_current_step()
        formatted = wizard.format_step(step)
        
        assert step['title'] in formatted
        assert 'Step 1 of' in formatted


# =============================================================================
# Pass 133: Validation Feedback System Tests
# =============================================================================

class TestValidationFeedback:
    """Test validation feedback."""
    
    def test_add_error(self):
        """Test adding validation error."""
        vf = ValidationFeedback()
        vf.add_error('email', 'Invalid email format')
        
        assert vf.has_errors() is True
    
    def test_add_warning(self):
        """Test adding validation warning."""
        vf = ValidationFeedback()
        vf.add_warning('password', 'Weak password')
        
        assert vf.has_warnings() is True
    
    def test_clear(self):
        """Test clearing validation messages."""
        vf = ValidationFeedback()
        vf.add_error('field', 'error')
        vf.clear()
        
        assert vf.has_errors() is False
    
    def test_format_feedback(self):
        """Test feedback formatting."""
        vf = ValidationFeedback()
        vf.add_error('email', 'Required')
        vf.add_warning('password', 'Weak')
        
        formatted = vf.format_feedback()
        assert 'Errors:' in formatted
        assert 'Warnings:' in formatted


# =============================================================================
# Pass 134: Audit Trail Visualization Tests
# =============================================================================

class TestAuditTrailVisualizer:
    """Test audit trail visualization."""
    
    def test_add_entry(self):
        """Test adding audit entry."""
        visualizer = AuditTrailVisualizer()
        visualizer.add_entry('LOGIN', 'admin', 'Successful login')
        
        assert len(visualizer._entries) == 1
        assert visualizer._entries[0]['action'] == 'LOGIN'
    
    def test_format_timeline(self):
        """Test timeline formatting."""
        visualizer = AuditTrailVisualizer()
        visualizer.add_entry('SCAN', 'user1')
        visualizer.add_entry('REPORT', 'user2')
        
        timeline = visualizer.format_timeline()
        assert 'Audit Trail:' in timeline
        assert 'user1' in timeline
        assert 'user2' in timeline
    
    def test_format_summary(self):
        """Test summary formatting."""
        visualizer = AuditTrailVisualizer()
        visualizer.add_entry('ACTION', 'user')
        
        summary = visualizer.format_summary()
        assert 'Total audit events: 1' in summary


# =============================================================================
# Pass 135: Export Preview System Tests
# =============================================================================

class TestExportPreview:
    """Test export preview functionality."""
    
    def test_preview_json(self):
        """Test JSON export preview."""
        preview = ExportPreview()
        data = {'name': 'Test', 'value': 123}
        
        result = preview.preview(data, 'json')
        assert 'JSON Preview:' in result
        assert '"name": "Test"' in result
    
    def test_preview_csv(self):
        """Test CSV export preview."""
        preview = ExportPreview()
        data = [{'name': 'A', 'value': 1}, {'name': 'B', 'value': 2}]
        
        result = preview.preview(data, 'csv')
        assert 'CSV Preview:' in result
        assert 'name,value' in result or 'name,value' in result.replace(' ', '')
    
    def test_preview_pdf(self):
        """Test PDF export preview."""
        preview = ExportPreview()
        data = [{'item': 1}, {'item': 2}]
        
        result = preview.preview(data, 'pdf')
        assert 'PDF Preview:' in result
        assert '2 items' in result


# =============================================================================
# Pass 136: Batch Operation Manager Tests
# =============================================================================

class TestBatchOperationManager:
    """Test batch operations."""
    
    def test_add_operation(self):
        """Test adding batch operation."""
        manager = BatchOperationManager()
        callback = Mock(return_value='success')
        
        manager.add_operation('Test', callback, ['a', 'b', 'c'])
        assert len(manager._operations) == 1
    
    def test_execute_batch(self):
        """Test executing batch operations."""
        manager = BatchOperationManager()
        callback = Mock(return_value='success')
        
        manager.add_operation('Test', callback, ['a', 'b'])
        
        # Execute and collect progress updates
        updates = list(manager.execute())
        
        assert len(updates) == 2
        assert callback.call_count == 2
    
    def test_get_summary(self):
        """Test batch summary."""
        manager = BatchOperationManager()
        callback = Mock(return_value='success')
        
        manager.add_operation('Test', callback, ['a', 'b', 'c'])
        list(manager.execute())
        
        summary = manager.get_summary()
        assert summary['total'] == 3
        assert summary['successful'] == 3


# =============================================================================
# Pass 137: Data Backup and Restore Tests
# =============================================================================

class TestBackupManager:
    """Test backup and restore."""
    
    def test_create_backup(self, tmp_path):
        """Test creating backup."""
        backup_dir = str(tmp_path)
        manager = BackupManager(backup_dir)
        
        filepath = manager.create_backup({'key': 'value'}, 'test_backup')
        
        assert os.path.exists(filepath)
        assert 'test_backup' in filepath
    
    def test_list_backups(self, tmp_path):
        """Test listing backups."""
        backup_dir = str(tmp_path)
        manager = BackupManager(backup_dir)
        
        manager.create_backup({'data': 1}, 'backup1')
        manager.create_backup({'data': 2}, 'backup2')
        
        backups = manager.list_backups()
        assert len(backups) == 2
    
    def test_restore_backup(self, tmp_path):
        """Test restoring backup."""
        backup_dir = str(tmp_path)
        manager = BackupManager(backup_dir)
        
        original_data = {'config': 'value', 'nested': {'key': 'val'}}
        manager.create_backup(original_data, 'test')
        
        # Restore
        backups = manager.list_backups()
        restored = manager.restore_backup(backups[0]['filename'])
        
        assert restored == original_data


# =============================================================================
# Pass 138: Error Recovery System Tests
# =============================================================================

class TestErrorRecovery:
    """Test error recovery guidance."""
    
    def test_get_recovery_steps_connection(self):
        """Test connection error recovery."""
        guidance = ErrorRecovery.get_recovery_steps('connection_failed')
        
        assert 'connect' in guidance['message'].lower()
        assert len(guidance['steps']) > 0
    
    def test_get_recovery_steps_auth(self):
        """Test authentication error recovery."""
        guidance = ErrorRecovery.get_recovery_steps('authentication_failed')
        
        assert 'credentials' in guidance['message'].lower()
    
    def test_format_recovery(self):
        """Test recovery formatting."""
        formatted = ErrorRecovery.format_recovery('timeout')
        
        assert 'Error:' in formatted
        assert 'Recovery steps:' in formatted
        assert '1.' in formatted


# =============================================================================
# Pass 139: Screen Reader Support Tests
# =============================================================================

class TestScreenReaderSupport:
    """Test screen reader support."""
    
    def test_format_heading(self):
        """Test heading formatting."""
        result = ScreenReaderSupport.format_heading('Section Title', 2)
        assert 'Heading level 2' in result
        assert 'Section Title' in result
    
    def test_format_list(self):
        """Test list formatting."""
        items = ['First', 'Second', 'Third']
        result = ScreenReaderSupport.format_list(items, 'numbered')
        
        assert '1 of 3' in result
        assert '3 of 3' in result
    
    def test_format_table(self):
        """Test table formatting."""
        headers = ['Name', 'Status']
        rows = [['Device A', 'Online'], ['Device B', 'Offline']]
        
        result = ScreenReaderSupport.format_table(headers, rows)
        assert 'Table:' in result
        assert 'Row 1:' in result
        assert 'Device A' in result
    
    def test_announce_change(self):
        """Test change announcement."""
        result = ScreenReaderSupport.announce_change('Data updated')
        assert '[Update]' in result
        assert 'Data updated' in result


# =============================================================================
# Pass 140: Configuration Wizard Tests
# =============================================================================

class TestConfigurationWizard:
    """Test configuration wizard."""
    
    def test_wizard_steps(self):
        """Test wizard has multiple steps."""
        wizard = ConfigurationWizard()
        step = wizard.get_current_step()
        
        assert step is not None
        assert 'fields' in step
        assert step['total_steps'] > 1
    
    def test_set_field_value(self):
        """Test setting field values."""
        wizard = ConfigurationWizard()
        wizard.set_field_value('company_name', 'Test Corp')
        
        config = wizard.get_configuration()
        assert config['company_info']['company_name'] == 'Test Corp'
    
    def test_step_navigation(self):
        """Test wizard navigation."""
        wizard = ConfigurationWizard()
        
        initial_step = wizard.get_current_step()['step_number']
        wizard.next_step()
        next_step = wizard.get_current_step()['step_number']
        
        assert next_step == initial_step + 1
        
        wizard.previous_step()
        assert wizard.get_current_step()['step_number'] == initial_step


# =============================================================================
# Pass 141: Quick Action Shortcuts Tests
# =============================================================================

class TestQuickActions:
    """Test quick action shortcuts."""
    
    def test_get_action(self):
        """Test getting action by key."""
        action = QuickActions.get_action('F1')
        assert action['name'] == 'Help'
    
    def test_get_action_invalid(self):
        """Test getting invalid action."""
        action = QuickActions.get_action('INVALID')
        assert action is None
    
    def test_format_cheatsheet(self):
        """Test cheatsheet formatting."""
        sheet = QuickActions.format_cheatsheet()
        
        assert 'Quick Actions Reference:' in sheet
        assert 'F1' in sheet
        assert 'Help' in sheet


# =============================================================================
# Pass 142: User Feedback Collector Tests
# =============================================================================

class TestFeedbackCollector:
    """Test user feedback collection."""
    
    def test_submit_feedback(self, tmp_path):
        """Test submitting feedback."""
        storage = str(tmp_path / 'feedback.json')
        collector = FeedbackCollector(storage)
        
        collector.submit_feedback('usability', 'Great tool!', 5, 'Main menu')
        
        stats = collector.get_statistics()
        assert stats['usability'] == 1
    
    def test_get_statistics(self, tmp_path):
        """Test feedback statistics."""
        storage = str(tmp_path / 'feedback.json')
        collector = FeedbackCollector(storage)
        
        collector.submit_feedback('bug', 'Issue found')
        collector.submit_feedback('bug', 'Another issue')
        collector.submit_feedback('feature', 'New idea')
        
        stats = collector.get_statistics()
        assert stats['bug'] == 2
        assert stats['feature'] == 1
    
    def test_format_feedback_summary(self, tmp_path):
        """Test feedback summary formatting."""
        storage = str(tmp_path / 'feedback.json')
        collector = FeedbackCollector(storage)
        collector.submit_feedback('usability', 'Test')
        
        summary = collector.format_feedback_summary()
        assert 'Your Feedback History:' in summary
        assert 'Usability: 1 items' in summary


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
