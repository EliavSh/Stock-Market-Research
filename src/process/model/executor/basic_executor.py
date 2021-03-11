import numpy as np
import tensorflow as tf

from .evaluator import Evaluator
from .abstract_executor import AbstractExecutor
from ..hats_model.config import Config
from ..model_enum import ModelEnum


class BasicExecutor(AbstractExecutor):
    def __init__(self, sess, writer, model: ModelEnum, data_set, symbols):
        self.sess = sess
        self.writer = writer

        self.data_set = data_set
        self.model = model.get(sess, writer, symbols)
        self.evaluator = Evaluator(n_labels=Config.num_classes)

        self.n_epochs = Config.n_epochs
        # TODO - write n_epochs and num_classes in another config! the executor shouldn't get the hats' config!!!

        self.summary = tf.Summary()
        self.scalars = []

    def train_epoch(self, cur_epoch):
        labels = []
        losses, accs, cpt_accs, pred_rates, mac_f1, mic_f1, exp_rts = [], [], [], [], [], [], []
        accs_k, cpt_accs_k, pred_rates_k, mac_f1_k, mic_f1_k, exp_rts_k = [], [], [], [], [], []

        loss_for_tb, class_prob_for_tb = [[]], [[]]
        for (j, timestamp_data) in enumerate(zip(self.data_set)):
            x, y, rt = timestamp_data[0]
            my_loss, metrics = self.train_step(x, y, rt, cur_epoch, j)
            metrics_all, metrics_topk = metrics

            # loss_for_tb[0].append(loss)
            # class_prob_for_tb[0].append(metrics_all[0])
            # if j == 0 and cur_epoch == 0:
            #     self.add_scalar_to_summary("train_loss", loss_for_tb)

            #     for i, class_prediction in enumerate(class_prob_for_tb):
            #         self.add_scalar_to_summary("train_pred_class_" + str(i), class_prediction)

            losses.append(my_loss)

            # self.summary.value.add(tag="train_loss", simple_value=my_loss)
            # for i, class_prediction in enumerate(metrics_all[0]):
            #     self.summary.value.add(tag="train_pred_class_" + str(i), simple_value=class_prediction)

            # self.writer.add_summary(self.summary, cur_epoch * len(self.data_set) + j)

            # [s] = self.sess.run([tf.summary.scalar()])
            # self.writer.add_summary(s, cur_epoch * len(all_x) + j)
            # pred_rates.append(metrics_all[0])
            # for i, class_prediction in enumerate(metrics_all[0]):
            #     self.add_scalar_to_summary("train_pred_class_" + str(i), class_prediction)
            #
            # accs.append(metrics_all[1][0])
            # self.add_scalar_to_summary("train_accuracy", metrics_all[1][0])
            #
            # cpt_accs.append(metrics_all[1][1])
            # self.add_scalar_to_summary("train_compact_accuracy", metrics_all[1][1])
            #
            # mac_f1.append(metrics_all[2])
            # self.add_scalar_to_summary("train_macro_f1", metrics_all[2])
            #
            # mic_f1.append(metrics_all[3])
            # self.add_scalar_to_summary("train_micro_f1", metrics_all[3])
            #
            # exp_rts.append(metrics_all[4])
            # self.add_scalar_to_summary("train_expected_return", metrics_all[3])

            # [s] = self.sess.run([self.scalars])
            # list(map(lambda scalar: self.writer.add_summary(scalar, cur_epoch * len(self.data_set) + j), s))

            pred_rates_k.append(metrics_topk[0])
            accs_k.append(metrics_topk[1][0])
            cpt_accs_k.append(metrics_topk[1][1])
            mac_f1_k.append(metrics_topk[2])
            mic_f1_k.append(metrics_topk[3])
            exp_rts_k.append(metrics_topk[4])

        report_all = [np.around(np.array(pred_rates).mean(0), decimals=4), np.mean(accs), np.mean(cpt_accs), np.mean(mac_f1), np.mean(mic_f1), np.mean(exp_rts)]
        report_topk = [np.around(np.array(pred_rates_k).mean(0), decimals=4), np.mean(accs_k), np.mean(cpt_accs_k), np.mean(mac_f1_k), np.mean(mic_f1_k),
                       np.mean(exp_rts_k)]
        loss = np.mean(losses)
        cur_it = self.model.global_step_tensor.eval(self.sess)  # TODO remove the global variables
        return losses, report_all, report_topk

    def add_scalar_to_summary(self, name, value):
        self.scalars.append(tf.summary.scalar(name, value))

    def train_step(self, x, y, rt, cur_epoch, j):
        # batch is whole dataset of a single company
        feed_dict = {self.model.x: x, self.model.y: y}
        summary = tf.summary.merge_all()
        _, loss, pred, prob, s = self.sess.run([self.model.optimize, self.model.cross_entropy,
                                                self.model.prediction, self.model.prob, summary],
                                               feed_dict=feed_dict)
        self.writer.add_summary(s, cur_epoch * len(self.data_set) + j)

        label = np.argmax(y, 1)
        metrics = self.evaluator.metric(label, pred, prob, rt)

        return loss, metrics

    def train(self):
        te_loss_hist, te_acc_hist, te_acc_k_hist = [], [], []
        prev = -1
        all_losses = []
        for cur_epoch in range(self.model.cur_epoch_tensor.eval(self.sess), self.n_epochs + 1, 1):
            losses, report_all, report_topk = self.train_epoch(cur_epoch)
            self.sess.run(self.model.increment_cur_epoch_tensor)
            all_losses.append(losses)
        print('king')

    def test(self):
        pass
