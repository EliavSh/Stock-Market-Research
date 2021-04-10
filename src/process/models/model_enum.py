from enum import Enum
from .hats_model.hats import HATS
from .abstract_model import AbstractModel


class ModelEnum(Enum):
    HATS = HATS

    def get(self, *args) -> AbstractModel:
        return self.value(*args)
