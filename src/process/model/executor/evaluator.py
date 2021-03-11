# TODO turn this class to package
from sklearn.metrics import confusion_matrix
from sklearn.metrics import f1_score
import numpy as np


class Evaluator:
    def __init__(self, n_labels):
        self.n_labels = n_labels

    def get_f1(self, y, y_):
        # y : label | y_ : pred
        return f1_score(y, y_, average='macro'), f1_score(y, y_, average='micro')

    def get_acc(self, conf_mat):
        accuracy = conf_mat.trace() / conf_mat.sum()
        if self.n_labels == 2:
            compact_accuracy = accuracy
        else:
            # It is actually a recall of up down
            compact_conf_mat = np.take(conf_mat, [[0, 2], [6, 8]])
            compact_accuracy = compact_conf_mat.trace() / compact_conf_mat.sum()
        return accuracy, compact_accuracy

    def expected_return(self, pred, prob, returns):
        # To create neuralized portfolio
        n_mid = prob.shape[0] // 2
        # sorted : ascending order (based on down probabilty)
        # both side have exactly the half size of the universe
        short_half_idx = np.argsort(prob[:, 0])[-n_mid:]
        long_half_idx = np.argsort(prob[:, -1])[-n_mid:]
        # if prediction was neutral, we don'y count it as our return
        short_rts = (returns[short_half_idx] * (pred[short_half_idx] == 0)).mean() * (-1)
        long_rts = (returns[long_half_idx] * (pred[long_half_idx] == (self.n_labels - 1))).mean()
        return (short_rts + long_rts) * 100

    def filter_topk(self, label, pred, prob, returns, topk):
        short_k_idx = np.argsort(prob[:, 0])[-topk:]
        long_k_idx = np.argsort(prob[:, -1])[-topk:]
        topk_idx = np.concatenate([short_k_idx, long_k_idx])
        return label[topk_idx], pred[topk_idx], prob[topk_idx], returns[topk_idx]

    def cal_metric(self, label, pred, prob, returns):
        exp_returns = self.expected_return(pred, prob, returns)
        conf_mat = confusion_matrix(label, pred, labels=[i for i in range(self.n_labels)])
        acc, cpt_acc = self.get_acc(conf_mat)
        mac_f1, mic_f1 = self.get_f1(label, pred)
        pred_rate = [(pred == i).sum() / pred.shape[0] for i in range(self.n_labels)]
        return pred_rate, (acc, cpt_acc), mac_f1, mic_f1, exp_returns

    def metric(self, label, pred, prob, returns, topk=30):
        metric_all = self.cal_metric(label, pred, prob, returns)
        label, pred, prob, returns = self.filter_topk(label, pred, prob, returns, topk)
        metric_topk = self.cal_metric(label, pred, prob, returns)
        return metric_all, metric_topk
