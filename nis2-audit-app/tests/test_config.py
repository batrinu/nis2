import unittest
from unittest.mock import patch, MagicMock
from pathlib import Path
import sys
import os
import shutil
import tempfile
from app.config import (
    is_portable_mode, 
    get_config_directory, 
    get_data_directory,
    PORTABLE_MARKER,
    PORTABLE_PYTHON_DIR,
    PORTABLE_DATA_DIR
)

class TestConfig(unittest.TestCase):
    def setUp(self):
        self.test_dir = Path(tempfile.mkdtemp())
        self.app_root = self.test_dir / "app"
        self.bin_dir = self.app_root / "bin"
        self.bin_dir.mkdir(parents=True)
        self.executable = str(self.bin_dir / "nis2-audit.exe")
        
        # Mock sys.executable to point to our temp executable
        self.patcher_exe = patch('sys.executable', self.executable)
        self.patcher_exe.start()

    def tearDown(self):
        self.patcher_exe.stop()
        shutil.rmtree(self.test_dir)

    def test_is_portable_mode_no_marker(self):
        """Test that portable mode is False when no markers exist."""
        self.assertFalse(is_portable_mode())

    def test_is_portable_mode_with_marker_file(self):
        """Test that portable mode is True when .portable file exists."""
        (self.app_root / PORTABLE_MARKER).touch()
        self.assertTrue(is_portable_mode())

    def test_is_portable_mode_with_python_dir(self):
        """Test that portable mode is True when python/ directory exists."""
        (self.app_root / PORTABLE_PYTHON_DIR).mkdir()
        self.assertTrue(is_portable_mode())

    def test_get_config_directory_portable(self):
        """Test config directory resolution in portable mode."""
        (self.app_root / PORTABLE_MARKER).touch()
        config_dir = get_config_directory()
        expected = self.app_root / PORTABLE_DATA_DIR / 'config'
        self.assertEqual(config_dir, expected)
        self.assertTrue(config_dir.exists())

    def test_get_data_directory_portable(self):
        """Test data directory resolution in portable mode."""
        (self.app_root / PORTABLE_MARKER).touch()
        data_dir = get_data_directory()
        expected = self.app_root / PORTABLE_DATA_DIR
        self.assertEqual(data_dir, expected)
        self.assertTrue(data_dir.exists())

    def test_get_config_directory_non_portable_current_platform(self):
        """Test config directory resolution in non-portable mode on current platform."""
        with patch('app.config.is_portable_mode', return_value=False):
            config_dir = get_config_directory()
            # On Linux, it should be in .config or XDG_CONFIG_HOME
            if sys.platform == 'linux':
                expected_base = os.environ.get('XDG_CONFIG_HOME') or os.path.expanduser('~/.config')
                self.assertTrue(str(config_dir).startswith(str(expected_base)))
            self.assertTrue(str(config_dir).endswith('nis2-audit'))

if __name__ == '__main__':
    unittest.main()
