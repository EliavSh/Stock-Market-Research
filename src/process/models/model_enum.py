from enum import Enum
from .hats_model.hats_tensor_flow_v1 import HatsTensorFlowV1
from .hats_model.hats_tensor_flow_v2 import HatsTensorFlowV2
from .abstract_model import AbstractModel


class ModelEnum(Enum):
    HatsTensorFlowV1 = HatsTensorFlowV1
    HatsTensorFlowV2 = HatsTensorFlowV2

    def get(self, *args) -> AbstractModel:
        return self.value(*args)
