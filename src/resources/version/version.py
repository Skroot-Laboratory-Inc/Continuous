import json
import os
import platform
from enum import Enum

from src.app.ui_manager.theme_enum import Theme


class DevelopmentVersion(Enum):
    Dev = "Dev"
    Test = "Test"
    Production = "Prod"


class UseCase(Enum):
    Continuous = "Manufacturing"
    FlowCell = "FlowCell"
    SkrootFlowCell = "SkrootFlowCell"
    Tunair = "Tunair"
    RollerBottle = "RollerBottle"


class Version:
    _inMemoryUseCase = None

    def __init__(self):
        self.major = 3.0
        self.minor = 10
        self.developmentVersion = DevelopmentVersion.Test
        self.isBeta = True

        self.use_case_themes = {
            UseCase.Continuous:     Theme.WW,
            UseCase.FlowCell:       Theme.IBI,
            UseCase.SkrootFlowCell: Theme.Skroot,
            UseCase.Tunair:         Theme.IBI,
            UseCase.RollerBottle:   Theme.Skroot,
        }

        self.deviceConfigPath = "/etc/skroot/device_config.json"
        self.useCase = self._resolveUseCase()
        self.theme = self.use_case_themes[self.useCase] if self.useCase else None

    def _resolveUseCase(self):
        """Resolve use case from in-memory override or device_config.json.
        On Windows, only the in-memory override is used so the product selection
        dialog is shown on every launch without persisting to disk.
        Returns None if not configured."""
        if Version._inMemoryUseCase is not None:
            return Version._inMemoryUseCase
        if platform.system() == "Windows":
            return None
        if not os.path.exists(self.deviceConfigPath):
            return None
        try:
            with open(self.deviceConfigPath, 'r') as f:
                config = json.load(f)
            use_case_str = config.get("use_case")
            if not use_case_str:
                return None
            # Try matching by value first (e.g., "Manufacturing"), then by name (e.g., "Continuous")
            try:
                return UseCase(use_case_str)
            except ValueError:
                return UseCase[use_case_str]
        except (json.JSONDecodeError, KeyError, FileNotFoundError):
            return None

    @staticmethod
    def setInMemoryUseCase(use_case: UseCase):
        """Store the selected use case in memory only (no file write).
        Used on Windows to avoid persisting dev selections to disk."""
        Version._inMemoryUseCase = use_case

    @staticmethod
    def setDeviceUseCase(use_case: UseCase):
        """Write the selected use case to the device config file and update Plymouth boot theme."""
        import logging
        config_path = "/etc/skroot/device_config.json"
        try:
            os.makedirs(os.path.dirname(config_path), exist_ok=True)
            with open(config_path, 'w') as f:
                json.dump({"use_case": use_case.value}, f, indent=2)
        except PermissionError:
            logging.exception(
                f"Permission denied writing to {config_path}. "
                f"Ensure /etc/skroot is owned by the application user. "
                f"Falling back to in-memory selection.",
                extra={"id": "System failure"}
            )
            Version._inMemoryUseCase = use_case
            return

        # Update Plymouth boot splash to match the selected use case
        theme_map = {
            UseCase.Continuous:     Theme.WW,
            UseCase.FlowCell:       Theme.IBI,
            UseCase.SkrootFlowCell: Theme.Skroot,
            UseCase.Tunair:         Theme.IBI,
            UseCase.RollerBottle:   Theme.Skroot,
        }
        theme = theme_map.get(use_case)
        if theme:
            try:
                import subprocess
                subprocess.run(
                    ["sudo", "plymouth-set-default-theme", theme.value],
                    check=True, timeout=10
                )
                subprocess.run(
                    ["sudo", "update-initramfs", "-u"],
                    check=True, timeout=120
                )
            except Exception:
                pass  # Plymouth may not be available in dev/CI environments

    @staticmethod
    def getAllUseCases() -> list:
        """Return all UseCase enum members."""
        return list(UseCase)

    def getMajorVersion(self) -> float:
        return self.major

    def getMinorVersion(self) -> int:
        return self.minor

    def getVersionString(self) -> str:
        return f"{self.major}.{self.minor}"

    def getReleaseNotesFilePath(self) -> str:
        """Get the file path for release notes of a specific use case"""
        return f"../resources/version/release_notes/{self.getUseCase()}.json"

    def getUseCase(self) -> str:
        return self.useCase.value

    def getDevelopmentVersion(self):
        return self.developmentVersion.value

    def getTheme(self) -> Theme:
        return self.theme

    def getReleaseBucket(self) -> str:
        if self.isBeta:
            return f"{self.getUseCase()}/{self.getDevelopmentVersion()}/Beta"
        else:
            return f"{self.getUseCase()}/{self.getDevelopmentVersion()}"
