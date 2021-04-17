from src.process.models.abstract_model import AbstractModel
from src.process.models.hats_model.hats_utils.model_parameters import ModelParams


class HatsTensorFlowV2(AbstractModel):
    def __init__(self, writer, symbols, config):
        super().__init__(config)
        self.params = ModelParams(symbols)

    def build_model(self):
        pass
