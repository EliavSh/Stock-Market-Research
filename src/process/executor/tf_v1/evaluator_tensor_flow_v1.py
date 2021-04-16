# TODO turn this class to package
from sklearn.metrics import confusion_matrix
from sklearn.metrics import f1_score
import numpy as np
import tensorflow as tf


class EvaluatorTensorFlowV1:
    def __init__(self, sess, n_labels, model, top_k_percent):
        self.sess = sess
        self.n_labels = n_labels
        self.model = model
        self.top_k_percent = top_k_percent

        self.rates = tf.placeholder(tf.float32, shape=[self.model.params.num_companies], name='rates')
        self.increase_class = tf.cast(tf.placeholder_with_default(input=self.n_labels - 1, shape=(), name='increase_class'), tf.dtypes.int64)
        self.decrease_class = tf.cast(tf.placeholder_with_default(input=0, shape=(), name='decrease_class'), tf.dtypes.int64)

        self.train_summaries = self.train_summary()
        self.test_summaries = self.test_summary()

    def train_summary(self):
        with tf.name_scope('train_summary'):
            summaries = [tf.summary.scalar('train_entropy_loss', self.model.cross_entropy),
                         # take the top-k-companies and record the ratio of model successful prediction with real movement
                         tf.summary.scalar('top_k_hit_ratio', self.calc_top_k(self.increase_class, tf.math.greater_equal(self.rates, 0.))),
                         # record the same for bottom-k-companies
                         tf.summary.scalar('bottom_k_hit_ratio', self.calc_top_k(self.decrease_class, tf.math.greater(0., self.rates)))]
        return summaries

    def test_summary(self):
        with tf.name_scope('test_summary'):
            summaries = [tf.summary.scalar('test_entropy_loss', self.model.cross_entropy),
                         # take the top-k-companies and record the ratio of model successful prediction with real movement
                         tf.summary.scalar('top_k_hit_ratio', self.calc_top_k(self.increase_class, tf.math.greater_equal(self.rates, 0.))),
                         # record the same for bottom-k-companies
                         tf.summary.scalar('bottom_k_hit_ratio', self.calc_top_k(self.decrease_class, tf.math.greater(0., self.rates)))]
        return summaries

    def calc_top_k(self, class_index, true_movement):
        # get the top companies probabilities
        top_indices = tf.where(tf.equal(self.model.prediction, class_index), name='top_indices')
        top_prob = tf.math.reduce_sum(tf.gather(self.model.prob, top_indices), axis=1)[:, class_index]

        # calc top k by model
        k = self.model.params.num_companies * self.top_k_percent
        # in case k passes the total companies of the movement, summary all of them
        corrected_k = k if top_indices.shape[0] >= k else tf.shape(top_indices, out_type=tf.int32)[0]
        top_k_indices = tf.argsort(top_prob, direction="DESCENDING")[:corrected_k]

        # finally, calculate success ratio of top k by true movement of the companies
        return tf.math.divide(tf.reduce_sum(tf.cast(tf.gather(true_movement, top_k_indices), dtype=tf.float32)), tf.cast(corrected_k, tf.float32))

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
