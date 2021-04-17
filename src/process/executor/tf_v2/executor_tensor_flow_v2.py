import numpy as np
from typing import List

from src.process.models.model_enum import ModelEnum
from src.process.executor.abstract_executor import AbstractExecutor


class ExecutorTensorFlowV2(AbstractExecutor):
    def __init__(self, model: ModelEnum, symbols, config):
        super().__init__(config)

        # TODO - create writer

        # TODO - create model
        self.model = model.get(symbols, config)

    def step(self, x: np.array, y: List, rt: np.array, cur_epoch: int, timestamp: int, len_data: int, phase: str):
        all_train_losses, all_test_losses = [], []
        for cur_epoch in range(self.n_epochs):
            pass
