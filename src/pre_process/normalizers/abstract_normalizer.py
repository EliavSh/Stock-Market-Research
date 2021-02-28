from abc import ABC, abstractmethod
from typing import Dict, List


class AbstractNormalizer(ABC):

    @abstractmethod
    def normalize(self, stocks_list: Dict[str, List[list]]) -> None:
        raise NotImplementedError
