# Copyright 2015 The TensorFlow Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================

"""Example / benchmark for building a PTB LSTM model.

Trains the model described in:
(Zaremba, et. al.) Recurrent Neural Network Regularization
http://arxiv.org/abs/1409.2329

There are 3 supported model configurations:
===========================================
| config | epochs | train | valid  | test
===========================================
| small  | 13     | 37.99 | 121.39 | 115.91
| medium | 39     | 48.45 |  86.16 |  82.07
| large  | 55     | 37.87 |  82.62 |  78.29
The exact results may vary depending on the random initialization.

The hyperparameters used in the model:
- init_scale - the initial scale of the weights
- learning_rate - the initial value of the learning rate
- max_grad_norm - the maximum permissible norm of the gradient
- num_layers - the number of LSTM layers
- num_steps - the number of unrolled steps of LSTM
- hidden_size - the number of LSTM units
- max_epoch - the number of epochs trained with the initial learning rate
- max_max_epoch - the total number of epochs for training
- keep_prob - the probability of keeping weights in the dropout layer
- lr_decay - the decay of the learning rate for each epoch after "max_epoch"
- batch_size - the batch size

The data required for this example is in the data/ dir of the
PTB dataset from Tomas Mikolov's webpage:

$ wget http://www.fit.vutbr.cz/~imikolov/rnnlm/simple-examples.tgz
$ tar xvf simple-examples.tgz

To run:

$ python ptb_word_lm.py --data_path=simple-examples/data/

"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import time
import math

import numpy as np
import tensorflow as tf

import reader

#train_opt = open("train_opt", 'w');
#valid_opt = open("valid_opt", 'w');

flags = tf.flags
logging = tf.logging

flags.DEFINE_string(
    "model", "small",
    "A type of model. Possible options are: small, medium, large.")
flags.DEFINE_string("data_path", None,
                    "Where the training/test data is stored.")
flags.DEFINE_string("save_path", None,
                    "Model output directory.")
flags.DEFINE_bool("use_fp16", False,
                  "Train using 16-bit floats instead of 32bit floats")

FLAGS = flags.FLAGS


def data_type():
  return tf.float16 if FLAGS.use_fp16 else tf.float32


class PTBInput(object):
  """The input data."""

  def __init__(self, config, data, name=None):
    self.batch_size = batch_size = config.batch_size
    self.num_steps = num_steps = config.num_steps
    self.epoch_size = ((len(data) // batch_size) - 1) // num_steps
    self.input_data, self.targets = reader.ptb_producer(
        data, batch_size, num_steps, name=name)


class PTBModel(object):
  """The PTB model."""

  


  def __init__(self, is_training, config, input_):
    self._input = input_

    batch_size = input_.batch_size
    num_steps = input_.num_steps
    size = config.hidden_size
    vocab_size = config.vocab_size

    # Slightly better results can be obtained with forget gate biases
    # initialized to 1 but the hyperparameters of the model would need to be
    # different than reported in the paper.

#    def lstm_cell():
#      return tf.contrib.rnn.BasicLSTMCell(
#          size, forget_bias=0.0, state_is_tuple=True)
    

    def get_random_indices(logitss,num_sampless):
      return tf.random_uniform([logitss.get_shape().as_list()[0],num_sampless],
        minval=0, maxval=logitss.get_shape().as_list()[1]-1, dtype=tf.int32, seed=0);

    def get_top_k_indices(logitss,k):
      top_k_logitss,top_k_indices=tf.nn.top_k(logitss,k);
      #top_k_logitss=tf.stop_gradient(top_k_logitss);
      top_k_indices=tf.stop_gradient(top_k_indices);
      return top_k_indices;

    def calcLoss(targetss,logitss,batch_sizee,num_sampless,num_stepss,indices):
      indices2=tf.zeros([num_sampless],tf.int32);
      print("indices2");
      print(indices2);

      #heightt=tf.to_int32(tf.shape(logitss)[0]);
      heightt=logitss.get_shape().as_list()[0];
      print("heightt");
      print(heightt);
      for i in range(1,heightt):
        #print("Loop Beginsssss");
        tempp=tf.fill([num_sampless],i);
        indices2=tf.concat(0,[indices2,tempp]);

      print("indices2");
      print(indices2);
      indices=indices2+tf.reshape(indices, [-1]);
      print("indices");
      print(indices);
      negative_logitss=tf.gather(tf.reshape(logitss, [-1]),indices);
      negative_logitss=tf.reshape(negative_logitss,[heightt,num_sampless]);
      
      print("logitss");
      print(logitss);
      print("negative_logitss");
      print(negative_logitss);
      print("indices");
      print(indices);
      print("targetss");
      print(targetss);
      targetss_flattened=tf.range(0,tf.shape(logitss)[0])*tf.shape(logitss)[1]+targetss;
      print("targetss_flattened");
      print(targetss_flattened);
      true_logitss = tf.gather(tf.reshape(logitss, [-1]),targetss_flattened);
      print("true_logitss");
      print(true_logitss);
      new_targetss=tf.zeros([logitss.get_shape().as_list()[0]],tf.int32);
      print("new_targetss");
      print(new_targetss);
      true_logitss_2d=tf.reshape(true_logitss,[tf.shape(true_logitss)[0],1]);
      print("true_logitss_2d");
      print(true_logitss_2d);

      print("new_logitss");
      new_logitss=tf.concat(1,[true_logitss_2d,negative_logitss]);
      print(new_logitss);
      
      

      loss = tf.nn.seq2seq.sequence_loss_by_example(
          [new_logitss],
          [new_targetss],
          [tf.ones([batch_sizee * num_stepss], dtype=data_type())])


      return loss;


    
    def lstm_cell():
      return tf.nn.rnn_cell.BasicLSTMCell(
          size, forget_bias=0.0, state_is_tuple=True) 

    attn_cell = lstm_cell
    if is_training and config.keep_prob < 1:
      def attn_cell():
        #return tf.contrib.rnn.DropoutWrapper(
        #    lstm_cell(), output_keep_prob=config.keep_prob)
        return tf.nn.rnn_cell.DropoutWrapper(
            lstm_cell(), output_keep_prob=config.keep_prob)
#    cell = tf.contrib.rnn.MultiRNNCell(
#        [attn_cell() for _ in range(config.num_layers)], state_is_tuple=True)

    cell = tf.nn.rnn_cell.MultiRNNCell(
        [attn_cell() for _ in range(config.num_layers)], state_is_tuple=True)

    self._initial_state = cell.zero_state(batch_size, data_type())

    with tf.device("/cpu:0"):
      embedding = tf.get_variable(
          "embedding", [vocab_size, size], dtype=data_type())
      inputs = tf.nn.embedding_lookup(embedding, input_.input_data)

    if is_training and config.keep_prob < 1:
      inputs = tf.nn.dropout(inputs, config.keep_prob)

    # Simplified version of models/tutorials/rnn/rnn.py's rnn().
    # This builds an unrolled LSTM for tutorial purposes only.
    # In general, use the rnn() or state_saving_rnn() from rnn.py.
    #
    # The alternative version of the code below is:
    #
    # inputs = tf.unstack(inputs, num=num_steps, axis=1)
    # outputs, state = tf.nn.rnn(cell, inputs,
    #                            initial_state=self._initial_state)
    outputs = []
    state = self._initial_state
    with tf.variable_scope("RNN"):
      for time_step in range(num_steps):
        if time_step > 0: tf.get_variable_scope().reuse_variables()
        (cell_output, state) = cell(inputs[:, time_step, :], state)
        outputs.append(cell_output)

    output = tf.reshape(tf.concat(1,outputs), [-1, size])
    softmax_w = tf.get_variable(
        "softmax_w", [size, vocab_size], dtype=data_type())
    softmax_w_t = tf.transpose(softmax_w);
    softmax_b = tf.get_variable("softmax_b", [vocab_size], dtype=data_type())

    use_sample_softmax=False;

    use_top_k_sample_softmax=False;
    use_random_sample_softmax=True;

    num_samples = 300;
    

    if is_training:
      if use_sample_softmax == True:
        print("use_sample_softmax");
#        w = tf.get_variable("proj_w", [size, vocab_size])
#        w_t = tf.transpose(w)
#        b = tf.get_variable("proj_b", [vocab_size])
        output_projection = (softmax_w, softmax_b)
        loss = tf.nn.sampled_softmax_loss(softmax_w_t, softmax_b, output, 
          tf.reshape(input_.targets, [-1, 1]), num_samples, vocab_size)

        logits = tf.matmul(output, softmax_w) + softmax_b;
        loss_full = tf.nn.seq2seq.sequence_loss_by_example(
            [logits],
            [tf.reshape(input_.targets, [-1])],
            [tf.ones([batch_size * num_steps], dtype=data_type())])
        self._cost_full = tf.reduce_sum(loss_full) / batch_size;

        self._cost = cost = tf.reduce_sum(loss) / batch_size;
        self._final_state = state

        print('Loss');
        print(loss);

        print('Cost');
        print(cost);
      elif use_top_k_sample_softmax:
        print("use_top_k_sample_softmax");
        logits = tf.matmul(output, softmax_w) + softmax_b
        '''
        loss = tf.contrib.legacy_seq2seq.sequence_loss_by_example(
            [logits],
            [tf.reshape(input_.targets, [-1])],
            [tf.ones([batch_size * num_steps], dtype=data_type())])
        '''
        probabilities=(tf.nn.softmax(logits));
        print("probabilities[0]");
        print(probabilities[0]);
        targetss=tf.reshape(input_.targets, [-1]);
        print("batch_size");
        print(batch_size);

        indices=get_top_k_indices(logits,num_samples);
        loss=calcLoss(targetss,logits,batch_size,num_samples,num_steps,indices);
        
        loss_full = tf.nn.seq2seq.sequence_loss_by_example(
            [logits],
            [tf.reshape(input_.targets, [-1])],
            [tf.ones([batch_size * num_steps], dtype=data_type())])
        self._cost_full = tf.reduce_sum(loss_full) / batch_size;
        
        print("[tf.reshape(input_.targets, [-1])]");
        print([tf.reshape(input_.targets, [-1])]);
        print("loss");
        print(loss);
        self._cost = cost = tf.reduce_sum(loss) / batch_size
        self._final_state = state
      elif use_random_sample_softmax:
        print("use_random_sample_softmax")
        logits = tf.matmul(output, softmax_w) + softmax_b
        '''
        loss = tf.contrib.legacy_seq2seq.sequence_loss_by_example(
            [logits],
            [tf.reshape(input_.targets, [-1])],
            [tf.ones([batch_size * num_steps], dtype=data_type())])
        '''
        probabilities=(tf.nn.softmax(logits));
        print("probabilities[0]");
        print(probabilities[0]);
        targetss=tf.reshape(input_.targets, [-1]);
        print("batch_size");
        print(batch_size);

        indices=get_random_indices(logits,num_samples);
        loss=calcLoss(targetss,logits,batch_size,num_samples,num_steps,indices);
        

        loss_full = tf.nn.seq2seq.sequence_loss_by_example(
            [logits],
            [tf.reshape(input_.targets, [-1])],
            [tf.ones([batch_size * num_steps], dtype=data_type())])
        self._cost_full = tf.reduce_sum(loss_full) / batch_size;


        print("[tf.reshape(input_.targets, [-1])]");
        print([tf.reshape(input_.targets, [-1])]);
        print("loss");
        print(loss);
        self._cost = cost = tf.reduce_sum(loss) / batch_size
        self._final_state = state
      else:
        print("No Sampling Training")
        logits = tf.matmul(output, softmax_w) + softmax_b
        #print([batch_size]);
        #print([num_steps]);
        #print([logits]);
        #print([tf.reshape(input_.targets, [-1])]);
        #print([tf.ones([batch_size * num_steps], dtype=data_type())]);
        loss = tf.nn.seq2seq.sequence_loss_by_example(
              [logits],
              [tf.reshape(input_.targets, [-1])],
              [tf.ones([batch_size * num_steps], dtype=data_type())])
        self._cost = cost = tf.reduce_sum(loss) / batch_size
        self._final_state = state
        self._cost_full = tf.reduce_sum(loss) / batch_size;
    else:
      print("No Sampling Testing")
      logits = tf.matmul(output, softmax_w) + softmax_b
      #print([batch_size]);
      #print([num_steps]);
      #print([logits]);
      #print([tf.reshape(input_.targets, [-1])]);
      #print([tf.ones([batch_size * num_steps], dtype=data_type())]);
      loss = tf.nn.seq2seq.sequence_loss_by_example(
            [logits],
            [tf.reshape(input_.targets, [-1])],
            [tf.ones([batch_size * num_steps], dtype=data_type())])
      self._cost = cost = tf.reduce_sum(loss) / batch_size
      self._final_state = state
      self._cost_full = tf.reduce_sum(loss) / batch_size;


    if not is_training:
      return

    self._lr = tf.Variable(0.0, trainable=False)
    tvars = tf.trainable_variables()
    grads, _ = tf.clip_by_global_norm(tf.gradients(cost, tvars),
                                      config.max_grad_norm)
    #optimizer = tf.train.GradientDescentOptimizer(self._lr)
    optimizer = tf.train.AdagradOptimizer(self._lr)
    self._train_op = optimizer.apply_gradients(
        zip(grads, tvars),
        global_step=tf.contrib.framework.get_or_create_global_step())

    self._new_lr = tf.placeholder(
        tf.float32, shape=[], name="new_learning_rate")
    self._lr_update = tf.assign(self._lr, self._new_lr)

  def assign_lr(self, session, lr_value):
    session.run(self._lr_update, feed_dict={self._new_lr: lr_value})

  @property
  def input(self):
    return self._input

  @property
  def initial_state(self):
    return self._initial_state

  @property
  def cost(self):
    return self._cost

  @property
  def cost_full(self):
    return self._cost_full

  @property
  def final_state(self):
    return self._final_state

  @property
  def lr(self):
    return self._lr

  @property
  def train_op(self):
    return self._train_op


class SmallConfig(object):
  """Small config."""
  init_scale = 0.1
#  learning_rate = 1.0
  learning_rate = 1.0
  max_grad_norm = 5
  num_layers = 2
  num_steps = 20
  hidden_size = 200
#  max_epoch = 4
  max_epoch = 4
#  max_max_epoch = 13
  max_max_epoch = 13
  keep_prob = 1.0
#  lr_decay = 0.5
  lr_decay = 0.5
  batch_size = 20
  vocab_size = 10000


class MediumConfig(object):
  """Medium config."""
  init_scale = 0.05
  learning_rate = 1.0
  max_grad_norm = 5
  num_layers = 2
  num_steps = 35
  hidden_size = 650
  max_epoch = 6
  max_max_epoch = 39
  keep_prob = 0.5
  lr_decay = 0.8
  batch_size = 20
  vocab_size = 10000


class LargeConfig(object):
  """Large config."""
  init_scale = 0.04
  learning_rate = 1.0
#  learning_rate = 0.0001
  max_grad_norm = 10
  num_layers = 2
  num_steps = 35
  hidden_size = 1500
  max_epoch = 14
  max_max_epoch = 55
  keep_prob = 0.35
  lr_decay = 1 / 1.15
  batch_size = 20
  vocab_size = 10000


class TestConfig(object):
  """Tiny config, for testing."""
  init_scale = 0.1
  learning_rate = 1.0
  max_grad_norm = 1
  num_layers = 1
  num_steps = 2
  hidden_size = 2
  max_epoch = 1
  max_max_epoch = 1
  keep_prob = 1.0
  lr_decay = 0.5
  batch_size = 20
  vocab_size = 10000


def run_epoch(session, model, eval_op=None, verbose=False):
  """Runs the model on the given data."""
  start_time = time.time()
  costs = 0.0
  costs_full=0.0;
  iters = 0
  state = session.run(model.initial_state)

  fetches = {
      "cost": model.cost,
      "final_state": model.final_state,
      "cost_full" : model.cost_full,
  }
  if eval_op is not None:
    fetches["eval_op"] = eval_op

  for step in range(model.input.epoch_size):
    feed_dict = {}
    for i, (c, h) in enumerate(model.initial_state):
      feed_dict[c] = state[i].c
      feed_dict[h] = state[i].h

    vals = session.run(fetches, feed_dict)
    cost = vals["cost"]
    state = vals["final_state"]
    cost_full=vals["cost_full"]

    costs += cost
    costs_full += cost_full;
    iters += model.input.num_steps


    if verbose and step % (model.input.epoch_size // 10) == 10:
      print(costs);
      print(iters);
#      print("%.3f perplexity: %.3f speed: %.0f wps" %
#            (step * 1.0 / model.input.epoch_size, np.exp(costs / iters),
#             iters * model.input.batch_size / (time.time() - start_time)))
      print("%.3f perplexity: %.3f speed: %.0f wps" %
            (step * 1.0 / model.input.epoch_size, np.exp(costs_full / iters),
             iters * model.input.batch_size / (time.time() - start_time)))

#  return np.exp(costs / iters)
  return np.exp(costs_full / iters)


def get_config():
  if FLAGS.model == "small":
    return SmallConfig()
  elif FLAGS.model == "medium":
    return MediumConfig()
  elif FLAGS.model == "large":
    return LargeConfig()
  elif FLAGS.model == "test":
    return TestConfig()
  else:
    raise ValueError("Invalid model: %s", FLAGS.model)


def main(_):
  if not FLAGS.data_path:
    raise ValueError("Must set --data_path to PTB data directory")

  raw_data = reader.ptb_raw_data(FLAGS.data_path)
  train_data, valid_data, test_data, _ = raw_data

  config = get_config()
  eval_config = get_config()
  eval_config.batch_size = 1
  eval_config.num_steps = 1

  with tf.Graph().as_default():
    initializer = tf.random_uniform_initializer(-config.init_scale,
                                                config.init_scale)

    with tf.name_scope("Train"):
      train_input = PTBInput(config=config, data=train_data, name="TrainInput")
      with tf.variable_scope("Model", reuse=None, initializer=initializer):
        m = PTBModel(is_training=True, config=config, input_=train_input)
      tf.scalar_summary("Training Loss", m.cost)
      tf.scalar_summary("Learning Rate", m.lr)

    with tf.name_scope("Valid"):
      valid_input = PTBInput(config=config, data=valid_data, name="ValidInput")
      with tf.variable_scope("Model", reuse=True, initializer=initializer):
        mvalid = PTBModel(is_training=False, config=config, input_=valid_input)
      tf.scalar_summary("Validation Loss", mvalid.cost)

    with tf.name_scope("Test"):
      test_input = PTBInput(config=eval_config, data=test_data, name="TestInput")
      with tf.variable_scope("Model", reuse=True, initializer=initializer):
        mtest = PTBModel(is_training=False, config=eval_config,
                         input_=test_input)

    sv = tf.train.Supervisor(logdir=FLAGS.save_path)
    train_arr=np.array([]);
    valid_arr=np.array([]);

    with sv.managed_session() as session:
      for i in range(config.max_max_epoch):
        lr_decay = config.lr_decay ** max(i + 1 - config.max_epoch, 0.0)
        m.assign_lr(session, config.learning_rate * lr_decay)

        print("Epoch: %d Learning rate: %.6f" % (i + 1, session.run(m.lr)))
        train_perplexity = run_epoch(session, m, eval_op=m.train_op,
                                     verbose=True)
        print("Epoch: %d Train Perplexity: %.3f" % (i + 1, train_perplexity))
        valid_perplexity = run_epoch(session, mvalid)
        print("Epoch: %d Valid Perplexity: %.3f" % (i + 1, valid_perplexity))
        train_arr=np.append(train_arr,[train_perplexity]);
        valid_arr=np.append(valid_arr,[valid_perplexity]);
        #print(train_arr);
        #print(valid_arr);
        print("train_arr");
        for itemm in train_arr:
          print(itemm);

        print("valid_arr");
        for itemm in valid_arr:
          print(itemm);

        #train_opt.write(tf.as_string(train_perplexity));
        #valid_opt.write(tf.as_string(valid_perplexity));
        #train_opt.write("\n");
        #valid_opt.write("\n");

        #np.savetxt('train_opt',tf.as_string(train_perplexity));

      test_perplexity = run_epoch(session, mtest)
      print("Test Perplexity: %.3f" % test_perplexity)

      if FLAGS.save_path:
        print("Saving model to %s." % FLAGS.save_path)
        sv.saver.save(session, FLAGS.save_path, global_step=sv.global_step)


if __name__ == "__main__":
  tf.app.run()
