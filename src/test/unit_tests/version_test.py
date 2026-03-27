import json
import os
import tempfile
import unittest
from unittest.mock import patch

from src.app.ui_manager.theme_enum import Theme
from src.resources.version.version import (
    DevelopmentVersion,
    UseCase,
    Version,
)


def _make_version_with_config(config_path):
    """Create a Version instance using a custom config path."""
    with patch("os.path.join", return_value=config_path):
        return Version()


class TestVersionThemeMapping(unittest.TestCase):

    def test_all_use_cases_have_theme(self):
        version = Version()
        for uc in UseCase:
            self.assertIn(uc, version.use_case_themes,
                          f"UseCase {uc.name} missing from use_case_themes")
            self.assertIsInstance(version.use_case_themes[uc], Theme)

    def test_theme_mapping_correctness(self):
        version = Version()
        expected = {
            UseCase.WWContinuous: Theme.WW,
            UseCase.SkrootContinuous: Theme.Skroot,
            UseCase.FlowCell: Theme.IBI,
            UseCase.SkrootFlowCell: Theme.Skroot,
            UseCase.Tunair: Theme.IBI,
            UseCase.RollerBottle: Theme.Skroot,
        }
        for uc, expected_theme in expected.items():
            self.assertEqual(version.use_case_themes[uc], expected_theme,
                             f"UseCase {uc.name} has wrong theme")

    def test_unified_version_across_use_cases(self):
        version = Version()
        self.assertIsInstance(version.major, float)
        self.assertIsInstance(version.minor, int)


class TestDeviceConfigResolution(unittest.TestCase):

    def _write_config(self, config_path, use_case_value):
        with open(config_path, 'w') as f:
            json.dump({"use_case": use_case_value}, f)

    def test_no_config_file_returns_none(self):
        config_path = "/tmp/_test_nonexistent_config.json"
        if os.path.exists(config_path):
            os.remove(config_path)
        version = _make_version_with_config(config_path)
        self.assertIsNone(version.useCase)
        self.assertIsNone(version.theme)

    def test_config_with_use_case_value(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({"use_case": "Manufacturing"}, f)
            config_path = f.name
        try:
            version = _make_version_with_config(config_path)
            self.assertEqual(version.useCase, UseCase.WWContinuous)
            self.assertEqual(version.theme, Theme.WW)
        finally:
            os.remove(config_path)

    def test_config_with_use_case_name(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({"use_case": "WWContinuous"}, f)
            config_path = f.name
        try:
            version = _make_version_with_config(config_path)
            self.assertEqual(version.useCase, UseCase.WWContinuous)
        finally:
            os.remove(config_path)

    def test_invalid_config_returns_none(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({"use_case": "InvalidProduct"}, f)
            config_path = f.name
        try:
            version = _make_version_with_config(config_path)
            self.assertIsNone(version.useCase)
        finally:
            os.remove(config_path)


class TestSetDeviceUseCase(unittest.TestCase):

    def test_set_and_read_device_use_case(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            config_path = f.name
        try:
            with patch("os.path.join", return_value=config_path):
                Version.setDeviceUseCase(UseCase.Tunair)
                version = Version()
                self.assertEqual(version.useCase, UseCase.Tunair)
                self.assertEqual(version.theme, Theme.IBI)
        finally:
            os.remove(config_path)


class TestGetAllUseCases(unittest.TestCase):

    def test_returns_all_six_use_cases(self):
        use_cases = Version.getAllUseCases()
        self.assertEqual(len(use_cases), 6)
        for uc in UseCase:
            self.assertIn(uc, use_cases)


class TestVersionGetters(unittest.TestCase):
    """Verify existing getter methods still work when use case is configured."""

    def test_getters_with_configured_use_case(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({"use_case": "FlowCell"}, f)
            config_path = f.name
        try:
            version = _make_version_with_config(config_path)
            self.assertEqual(version.getUseCase(), "FlowCell")
            self.assertEqual(version.getTheme(), Theme.IBI)
            self.assertIsInstance(version.getMajorVersion(), float)
            self.assertIsInstance(version.getMinorVersion(), int)
            self.assertIn(".", version.getVersionString())
            self.assertIn("FlowCell", version.getReleaseNotesFilePath())
            self.assertIn(version.getDevelopmentVersion(), ["Dev", "Test", "Prod"])
        finally:
            os.remove(config_path)


if __name__ == '__main__':
    unittest.main()
