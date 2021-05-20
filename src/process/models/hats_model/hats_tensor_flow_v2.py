from .hats_config import HatsConfig

from src.process.models.abstract_model import AbstractModel
from src.process.models.hats_model.hats_utils.model_parameters import ModelParams


class HatsTensorFlowV2(AbstractModel):
    def __init__(self, writer, symbols, config):
        super().__init__(config)

        # load from hats_config
        self.lr = HatsConfig.lr
        self.node_feat_size = HatsConfig.node_feat_size
        self.rel_attention = HatsConfig.rel_attention
        self.num_lstm_cells = HatsConfig.num_lstm_cells

        self.params = ModelParams(symbols)

    def build_model(self):
        """
        construct the relation representation to input representation

        """
        pass

    def forward(self):
        """
        1. get relation one hot and convert to input shape
        2. pass through num_lstm_cells cells of lstm
        lstm on inputs
        attention by graph
        """
