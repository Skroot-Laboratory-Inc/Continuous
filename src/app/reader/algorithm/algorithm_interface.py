from abc import abstractmethod, ABC

from src.app.model.result_set.result_set import ResultSet


class AlgorithmInterface(ABC):

    @abstractmethod
    def check(self, resultSet: ResultSet):
        """The prompts the algorithm to recalculate its status."""

    @abstractmethod
    def getStatus(self) -> bool:
        """Returns a bool reresentating the state of the algorithm."""
