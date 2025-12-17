"""Factory for creating UseCase-specific components."""
import platform
import tkinter as tk
from typing import Callable, Optional

from src.app.common_modules.authentication.session_manager.session_manager import SessionManager
from src.app.helper_methods.model.setup_reader_form_input import SetupReaderFormInput
from src.app.use_case.flow_cell.pump.pump_interface import PumpInterface
from src.app.use_case.flow_cell.pump.pump_manager import PumpManager
from src.app.reader.sib.sib_interface import SibInterface
from src.app.use_case.configuration.sib_properties import SibProperties
from src.app.ui_manager.root_manager import RootManager
from src.app.widget.kpi_form.kpi_form_base import KpiForm
from src.app.widget.setup_form.setup_form_base import SetupReaderForm
from src.resources.version.version import UseCase, Version

if platform.system() == "Windows":
    from src.app.use_case.flow_cell.pump.dev_pump import DevPump as PumpClass
else:
    from src.app.use_case.flow_cell.pump.pump import Pump as PumpClass


class ContextFactory:
    """
    Factory class that creates UseCase-specific components.

    This factory centralizes the creation of Sib, KpiForm, SetupForm, and other
    UseCase-dependent components based on the current Version().useCase setting.
    """

    def __init__(self, use_case: Optional[UseCase] = None):
        """
        Initialize the factory with a specific UseCase.

        Args:
            use_case: The UseCase to use. If None, uses Version().useCase
        """
        self.use_case = use_case if use_case is not None else Version().useCase

    def createSib(self, port, calibration_file: str, reader_number: int, port_allocator) -> SibInterface:
        """
        Create a Sib instance based on the current UseCase.

        Args:
            port: The serial port to use
            calibration_file: Path to the calibration file
            reader_number: The reader number
            port_allocator: The port allocator instance

        Returns:
            SibInterface implementation for the current UseCase

        Raises:
            Exception: If the UseCase is not supported
        """
        if self.use_case == UseCase.FlowCell:
            from src.app.use_case.flow_cell.flow_cell_sib import FlowCellSib
            return FlowCellSib(port, calibration_file, reader_number, port_allocator)
        elif self.use_case == UseCase.RollerBottle:
            from src.app.use_case.roller_bottle.roller_bottle_sib import RollerBottleSib
            return RollerBottleSib(port, calibration_file, reader_number, port_allocator)
        elif self.use_case == UseCase.Continuous:
            from src.app.use_case.continuous.continuous_sib import ContinuousSib
            return ContinuousSib(port, calibration_file, reader_number, port_allocator)
        elif self.use_case == UseCase.Tunair:
            from src.app.use_case.tunair.tunair_sib import TunairSib
            return TunairSib(port, calibration_file, reader_number, port_allocator)
        else:
            raise Exception(f"Unsupported use case for SIB instantiation: {self.use_case}")

    def createKpiForm(
        self,
        parent: tk.Frame,
        root_manager: RootManager,
        session_manager: SessionManager,
        pump_manager: Optional[PumpManager] = None
    ) -> KpiForm:
        """
        Create a KpiForm instance based on the current UseCase.

        Args:
            parent: The parent frame
            root_manager: The root manager instance
            session_manager: The session manager instance
            pump_manager: The pump manager (required for FlowCell, ignored otherwise)

        Returns:
            KpiForm implementation for the current UseCase

        Raises:
            Exception: If the UseCase is not supported
            ValueError: If FlowCell UseCase requires pump_manager but it's not provided
        """
        if self.use_case == UseCase.FlowCell:
            if pump_manager is None:
                raise ValueError("FlowCell UseCase requires a pump_manager")
            from src.app.use_case.flow_cell.flow_cell_kpi_form import FlowCellKpiForm
            return FlowCellKpiForm(parent, root_manager, session_manager, pump_manager)
        elif self.use_case == UseCase.RollerBottle:
            from src.app.use_case.roller_bottle.roller_bottle_kpi_form import RollerBottleKpiForm
            return RollerBottleKpiForm(parent, root_manager, session_manager)
        elif self.use_case == UseCase.Continuous:
            from src.app.use_case.continuous.continuous_kpi_form import ContinuousKpiForm
            return ContinuousKpiForm(parent, root_manager, session_manager)
        elif self.use_case == UseCase.Tunair:
            from src.app.use_case.tunair.tunair_kpi_form import TunairKpiForm
            return TunairKpiForm(parent, root_manager, session_manager)
        else:
            raise Exception(f"Unsupported use case for KPI form creation: {self.use_case}")

    def getSetupFormConfig(self):
        """
        Get the SetupFormConfig for the current UseCase.

        Returns:
            SetupFormConfig for the current UseCase

        Raises:
            Exception: If the UseCase is not supported
        """
        from src.app.use_case.configuration.setup_form_config import SetupFormConfig

        if self.use_case == UseCase.FlowCell:
            return SetupFormConfig.getFlowCellConfig()
        elif self.use_case == UseCase.RollerBottle:
            return SetupFormConfig.getRollerBottleConfig()
        elif self.use_case == UseCase.Continuous:
            return SetupFormConfig.getContinuousConfig()
        elif self.use_case == UseCase.Tunair:
            return SetupFormConfig.getTunairConfig()
        else:
            raise Exception(f"Unsupported use case for Setup form config: {self.use_case}")

    def createSetupForm(
        self,
        root_manager: RootManager,
        guided_setup_inputs: SetupReaderFormInput,
        parent: tk.Frame,
        submit_fn: Callable,
    ) -> SetupReaderForm:
        """
        Create a SetupReaderForm instance based on the current UseCase.

        Args:
            root_manager: The root manager instance
            guided_setup_inputs: The setup form input data
            parent: The parent frame
            submit_fn: The submit callback function

        Returns:
            SetupReaderForm implementation for the current UseCase

        Raises:
            Exception: If the UseCase is not supported
        """
        from src.app.widget.setup_form.configurable_setup_form import ConfigurableSetupForm

        config = self.getSetupFormConfig()
        return ConfigurableSetupForm(root_manager, guided_setup_inputs, parent, submit_fn, config)

    def getSibProperties(self):
        """
        Get SibProperties instance for the current UseCase.

        Returns:
            SibProperties instance (currently shared across all UseCases)
        """
        if self.use_case == UseCase.FlowCell:
            return SibProperties.getFlowCellProperties()
        elif self.use_case == UseCase.RollerBottle:
            return SibProperties.getRollerBottleProperties()
        elif self.use_case == UseCase.Continuous:
            return SibProperties.getContinuousProperties()
        elif self.use_case == UseCase.Tunair:
            return SibProperties.getTunairProperties()
        else:
            raise Exception(f"Unsupported use case for SIB instantiation: {self.use_case}")

    def requiresPump(self) -> bool:
        """
        Check if the current UseCase requires pump hardware.

        Returns:
            True if pump is required, False otherwise
        """
        return self.use_case == UseCase.FlowCell

    def createPump(self) -> Optional[PumpInterface]:
        """
        Create a pump instance if required by the UseCase.

        Returns:
            PumpInterface instance if required, None otherwise
        """
        if self.requiresPump():
            return PumpClass()
        return None

    def createPumpManager(self, pump: Optional[PumpInterface] = None) -> Optional[PumpManager]:
        """
        Create a PumpManager instance if required by the UseCase.

        Args:
            pump: Optional pump instance. If not provided and pump is required,
                  a new pump will be created.

        Returns:
            PumpManager instance if required, None otherwise
        """
        if self.requiresPump():
            if pump is None:
                pump = self.createPump()
            return PumpManager(pump)
        return None

    def showPumpControls(self) -> bool:
        """
        Check if the pump control popup should be shown for this UseCase.

        Returns:
            True if popup should be shown, False otherwise
        """
        return self.use_case == UseCase.FlowCell

    def showNextPageToggle(self) -> bool:
        """
        Check if the pump control popup should be shown for this UseCase.

        Returns:
            True if popup should be shown, False otherwise
        """
        return self.use_case == UseCase.Tunair or self.use_case == UseCase.Continuous or self.use_case == UseCase.RollerBottle

