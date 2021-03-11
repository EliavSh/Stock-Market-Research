from abc import abstractmethod, ABC


class AbstractExecutor(ABC):
    # TODO - remove this abstract class? we won't need another executor

    @abstractmethod
    def train(self):
        raise NotImplementedError

    def test(self):
        raise NotImplementedError
