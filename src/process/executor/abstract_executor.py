from abc import abstractmethod, ABC


class AbstractExecutor(ABC):
    # TODO - remove this abstract class? we won't need another executor

    @abstractmethod
    def start(self, *args):
        raise NotImplementedError
