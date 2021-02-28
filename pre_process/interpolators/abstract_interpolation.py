from abc import ABC, abstractmethod
from typing import Dict, List


class AbstractInterpolate(ABC):

    @abstractmethod
    def interpolate(self, stocks_data: Dict[str, List[List]]) -> Dict[str, List[List]]:
        raise NotImplementedError
