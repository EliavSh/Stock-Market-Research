from abc import ABC, abstractmethod


class AbstractFeature(ABC):
    @abstractmethod
    def add_feature(self, stocks_data):
        raise NotImplementedError
