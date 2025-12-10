
import pytest
from unittest.mock import MagicMock, patch
from local_kernel.wakeword.service import WakewordService

def test_wakeword_initialization():
    service = WakewordService(model_path="dummy/path")
    assert service.model_path == "dummy/path"
    assert service.is_listening is False

@patch("local_kernel.wakeword.service.KaldiRecognizer")
@patch("local_kernel.wakeword.service.Model")
@patch("local_kernel.wakeword.service.os.path.exists")
def test_wakeword_load_success(mock_exists, mock_model, mock_rec):
    mock_exists.return_value = True
    service = WakewordService()
    assert service.load_model() is True
    assert service.model is not None

@patch("local_kernel.wakeword.service.os.path.exists")
def test_wakeword_load_fail(mock_exists):
    mock_exists.return_value = False
    service = WakewordService()
    assert service.load_model() is False
