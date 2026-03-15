import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
from app.startup_checks import check_write_permissions, perform_startup_checks, StartupError

def test_check_write_permissions_success(tmp_path):
    """Test check_write_permissions returns True when directory is writable."""
    assert check_write_permissions(tmp_path) is True

def test_check_write_permissions_failure():
    """Test check_write_permissions returns False when directory is not writable."""
    # Using a path that definitely shouldn't be writable or doesn't exist in a way that touch fails
    # On many systems /root or a non-existent root-level dir will fail
    assert check_write_permissions(Path("/non_existent_and_no_permission")) is False

@patch("app.startup_checks.is_portable_mode")
@patch("app.startup_checks.get_data_directory")
@patch("app.startup_checks.check_python")
@patch("app.startup_checks.check_terminal_size")
def test_perform_startup_checks_portable_writable(mock_size, mock_python, mock_data_dir, mock_portable, tmp_path):
    """Test perform_startup_checks passes in portable mode when writable."""
    mock_python.return_value = (True, "python")
    mock_size.return_value = (True, 80, 24)
    mock_portable.return_value = True
    mock_data_dir.return_value = tmp_path
    
    # Should not raise StartupError
    perform_startup_checks()

@patch("app.startup_checks.is_portable_mode")
@patch("app.startup_checks.get_data_directory")
@patch("app.startup_checks.check_python")
@patch("app.startup_checks.check_terminal_size")
@patch("app.startup_checks.check_write_permissions")
def test_perform_startup_checks_portable_not_writable(mock_write, mock_size, mock_python, mock_data_dir, mock_portable):
    """Test perform_startup_checks fails in portable mode when not writable."""
    mock_python.return_value = (True, "python")
    mock_size.return_value = (True, 80, 24)
    mock_portable.return_value = True
    mock_data_dir.return_value = Path("/fake/path")
    mock_write.return_value = False
    
    with pytest.raises(StartupError) as excinfo:
        perform_startup_checks()
    
    assert "Write Permission Denied" in str(excinfo.value)
    assert "/fake/path" in str(excinfo.value)

@patch("app.startup_checks.is_portable_mode")
@patch("app.startup_checks.check_python")
@patch("app.startup_checks.check_terminal_size")
def test_perform_startup_checks_not_portable(mock_size, mock_python, mock_portable):
    """Test perform_startup_checks skips write check when not in portable mode."""
    mock_python.return_value = (True, "python")
    mock_size.return_value = (True, 80, 24)
    mock_portable.return_value = False
    
    # Should not call check_write_permissions or get_data_directory
    with patch("app.startup_checks.check_write_permissions") as mock_write:
        perform_startup_checks()
        mock_write.assert_not_called()
