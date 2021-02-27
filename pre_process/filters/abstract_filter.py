from abc import abstractmethod, ABC
from typing import List


class AbstractFilter(ABC):

    @abstractmethod
    def filter(self) -> List[str]:
        raise NotImplementedError
