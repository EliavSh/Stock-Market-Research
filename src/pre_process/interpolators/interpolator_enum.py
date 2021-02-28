from enum import Enum
from .basic_interpolator import BasicInterpolation


class InterpolationEnum(Enum):
    BasicInterpolation = BasicInterpolation
    # TODO - implement some more interpolations techniques

    def get(self):
        # The object instantiates only when calling it with 'get', instead of within the enum values
        return self.value()
