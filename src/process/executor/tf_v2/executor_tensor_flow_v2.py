from src.process.executor.abstract_executor import AbstractExecutor


class ExecutorTensorFlowV2(AbstractExecutor):
    def start(self, train_set, test_set):
        all_train_losses, all_test_losses = [], []
        for cur_epoch in range(100):
            pass
