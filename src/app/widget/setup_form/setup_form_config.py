"""Configuration for setup forms across different use cases."""
from dataclasses import dataclass
from typing import List


@dataclass
class SetupFormConfig:
    """Configuration for a setup form that defines which options are available."""

    scan_rate_options: List[str]
    equilibration_time_options: List[str]
    enable_pump_flow_rate: bool

    @staticmethod
    def get_continuous_config():
        """Configuration for Continuous (Manufacturing) use case."""
        return SetupFormConfig(
            scan_rate_options=["2", "5", "10", "30", "60"],
            equilibration_time_options=["0", "0.2", "2", "12", "24"],
            enable_pump_flow_rate=False
        )

    @staticmethod
    def get_flow_cell_config():
        """Configuration for FlowCell use case."""
        return SetupFormConfig(
            scan_rate_options=["2", "5", "10"],
            equilibration_time_options=["0", "0.2", "2", "12", "24"],
            enable_pump_flow_rate=True
        )

    @staticmethod
    def get_roller_bottle_config():
        """Configuration for RollerBottle use case."""
        return SetupFormConfig(
            scan_rate_options=["5", "10", "30", "60"],
            equilibration_time_options=["0", "0.2", "2", "12", "24"],
            enable_pump_flow_rate=False
        )

    @staticmethod
    def get_tunair_config():
        """Configuration for Tunair use case."""
        return SetupFormConfig(
            scan_rate_options=["5", "10"],
            equilibration_time_options=["0", "0.2", "2", "12", "24"],
            enable_pump_flow_rate=False
        )
