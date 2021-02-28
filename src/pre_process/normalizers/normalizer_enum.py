from enum import Enum
from .basic_normalizer import BasicNormalizer
from .abstract_normalizer import AbstractNormalizer


class NormalizerEnum(Enum):
    BasicNormalizer = BasicNormalizer

    def get(self) -> AbstractNormalizer:
        return self.value()
