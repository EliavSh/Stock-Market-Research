from abc import abstractmethod, ABC


class AbstractExecutor(ABC):

    @abstractmethod
    def start(self, *args):
        raise NotImplementedError
