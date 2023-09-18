from abc import ABC, abstractmethod
from ._batch import Batch


class Simulator(ABC):
    @abstractmethod
    def simulate_batch(batch: Batch) -> None:  # TODO results
        raise NotImplementedError()
