import tensorflow as tf

from ..abstract_model import AbstractModel
from .config import Config
from src.process.model.executor.evaluator import Evaluator
from .hats_utils.model_parameters import ModelParams


class HATS(AbstractModel):
    def __init__(self, sess, writer, symbols):
        super().__init__()
        # tensorflow and tensorboard initiators
        self.sess = sess
        self.writer = writer

        # construct essential classes
        self.params = ModelParams(symbols)
        self.evaluator = Evaluator(n_labels=Config.num_classes)

        # load from config
        self.n_epochs = Config.n_epochs
        self.features = Config.features
        self.input_dim = len(Config.features)
        self.look_back = Config.look_back
        self.n_labels = Config.num_classes
        self.lr = Config.lr
        self.node_feat_size = Config.node_feat_size
        self.rel_attention = Config.rel_attention

        # helper variables
        self.num_neighbors = tf.placeholder_with_default(Config.neighbors_sample, shape=(), name='num_neighbors')
        self.keep_prob = tf.placeholder_with_default(1 - Config.dropout, shape=(), name='keep_prob')

        self.build_model()

        # TODO - place it somewhere else -- must place it after build model?
        init = tf.group(tf.global_variables_initializer(), tf.local_variables_initializer())
        self.sess.run(init)

    def build_model(self):
        # TODO - build the model in another class? (the build model method)
        # x [num company, lookback]
        self.x = tf.placeholder(tf.float32, shape=[None, self.look_back, self.input_dim], name='x')
        self.y = tf.placeholder(tf.float32, shape=[None, self.n_labels], name='y')
        self.rel_mat = tf.convert_to_tensor(next(self.params.sample_neighbors()), dtype=tf.int32, name='relations_matrix')
        self.rel_num = tf.convert_to_tensor(self.params.summary_adjacency_matrix, dtype=tf.int32, name='relations_number')

        self.rel_emb = self.create_relation_onehot()

        self.exppanded = self.to_input_shape(self.rel_emb)

        state = self.get_state('lstm')
        # Graph operation
        self.all_rel_rep = self.get_relation_rep(state)

        # [Node, Feat dims]
        rel_summary = self.aggregate_relation_reps()
        updated_state = rel_summary + state[1:]

        logits = tf.layers.dense(inputs=updated_state, units=self.n_labels,
                                 activation=tf.nn.leaky_relu, name='logits')

        self.prob = tf.nn.softmax(logits, name='probability')
        self.prediction = tf.argmax(logits, -1, name='prediction')

        with tf.name_scope('loss'):
            self.cross_entropy = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(labels=self.y, logits=logits), name='cross_entropy')
            tf.summary.scalar('cross_entropy_loss', self.cross_entropy)

            reg_losses = tf.get_collection(tf.GraphKeys.REGULARIZATION_LOSSES)
            loss = self.cross_entropy
            update_ops = tf.get_collection(tf.GraphKeys.UPDATE_OPS)
            with tf.control_dependencies(update_ops):
                self.optimize = tf.train.AdamOptimizer(self.lr).minimize(loss, global_step=self.global_step_tensor)

            correct_prediction = tf.equal(tf.argmax(logits, -1), tf.argmax(self.y, -1))
            self.accuracy = tf.reduce_mean(tf.cast(correct_prediction, tf.float32))
        # self.loss = tf.summary.scalar('loss', self.cross_entropy)

    def get_state(self, state_module):
        if state_module == 'lstm':
            cells = [tf.contrib.rnn.BasicLSTMCell(self.node_feat_size) for _ in range(1)]
            dropout = [tf.contrib.rnn.DropoutWrapper(cell, input_keep_prob=self.keep_prob,
                                                     output_keep_prob=self.keep_prob) for cell in cells]
            lstm_cell = tf.nn.rnn_cell.MultiRNNCell(dropout, state_is_tuple=True)
            outputs, state = tf.nn.dynamic_rnn(lstm_cell, self.x, dtype=tf.float32)
            state = tf.concat([tf.zeros([1, state[-1][-1].shape[1]]), state[-1][-1]], 0)  # zero padding

        return state

    def get_relation_rep(self, state):
        # input state [Node, Original Feat Dims]
        with tf.variable_scope('get_relation_representation'):
            neighbors = tf.nn.embedding_lookup(state, self.rel_mat)
            # exp_state [1, Nodes, 1, Feat dims]
            exp_state = tf.expand_dims(tf.expand_dims(state[1:], 1), 0)
            exp_state = tf.tile(exp_state, [self.params.num_relation_types, 1, self.num_neighbors, 1])
            rel_embs = self.to_input_shape(self.rel_emb)

            # Concatenated (Neightbors with state) :  [Num Relations, Nodes, Num Max Neighbors, 2*Feat Dims]
            att_x = tf.concat([neighbors, exp_state, rel_embs], -1)

            score = tf.layers.dense(inputs=att_x, units=1, name='state_attention')
            att_mask_mat = tf.to_float(tf.expand_dims(tf.sequence_mask(self.rel_num, self.num_neighbors), -1))
            att_score = tf.nn.softmax(score, 2)
            all_rel_rep = tf.reduce_sum(neighbors * att_score, 2) / tf.expand_dims((tf.to_float(self.rel_num) + 1e-10), -1)

        return all_rel_rep

    def aggregate_relation_reps(self, ):
        def to_input_shape(emb):
            # [R,N,K,D]
            emb_ = []
            for i in range(emb.shape[0]):
                exp = tf.tile(tf.expand_dims(emb[i], 0), [self.params.num_companies, 1])
                emb_.append(tf.expand_dims(exp, 0))
            return tf.concat(emb_, 0)

        with tf.name_scope('aggregate_ops'):
            # all_rel_rep : [Num Relations, Nodes, Feat dims]
            if self.rel_attention:
                rel_emb = to_input_shape(self.rel_emb)
                att_x = tf.concat([self.all_rel_rep, rel_emb], -1)
                att_score = tf.nn.softmax(tf.layers.dense(inputs=att_x, units=1,
                                                          name='relation_attention'), 1)
                updated_state = tf.reduce_mean(self.all_rel_rep * att_score, 0)
            else:
                updated_state = tf.reduce_mean(self.all_rel_rep, 0)
        return updated_state

    def create_relation_onehot(self, ):
        one_hots = []
        for rel_idx in range(self.params.num_relation_types):
            one_hots.append(tf.one_hot([rel_idx], depth=self.params.num_relation_types))
        return tf.concat(one_hots, 0, name='relation_one-hot')

    def to_input_shape(self, emb):
        emb_ = []
        for i in range(emb.shape[0]):
            exp = tf.tile(tf.expand_dims(tf.expand_dims(emb[i], 0), 0), [self.params.num_companies, self.num_neighbors, 1])
            emb_.append(tf.expand_dims(exp, 0))
        return tf.concat(emb_, 0, name='to_input_shape')
