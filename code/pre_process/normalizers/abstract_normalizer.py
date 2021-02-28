from abc import ABC, abstractmethod
from typing import Dict, List


class AbstractNormalizer(ABC):

    @abstractmethod
    def normalize(self: Dict[str, List[list]]) -> Dict[str, List[list]]:
        raise NotImplementedError
