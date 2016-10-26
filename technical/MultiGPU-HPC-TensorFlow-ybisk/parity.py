import os,sys,math,datetime,random
import tensorflow as tf
import numpy as np

os.environ['CUDA_VISIBLE_DEVICES'] = '0,1'
gpu_list = [int(v) for v in os.environ['CUDA_VISIBLE_DEVICES'].split(',')]
print "Avilable GPUS: ", gpu_list

## Read the Data
D = [line.split() for line in open("data.txt")]
max_length = len(D[-1][0])
Input = np.zeros(shape=[len(D), max_length], dtype=np.int32)
for i in range(len(D)):
  for j in range(len(D[i])):
    Input[i][j] = D[i][j]
Label = np.reshape(np.array([[int(i) for i in v[1]] for v in D]), (len(D),2))


batch_size = 64
def get_batch():
  global batch_size
  idx = random.sample(range(len(D)), batch_size)
  return Input[idx], Label[idx]

class Model(object):
  def createModel(self, inputs, targets):
    l0 = tf.get_variable(name='FF-l0', shape=(self.max_length,1000), 
         initializer=tf.random_normal_initializer(stddev=1.0 / math.sqrt(self.max_length)))
    b0 = tf.get_variable(name='FF-b0', shape=(1000))
    l1 = tf.get_variable(name='FF-l1', shape=(1000,100), 
         initializer=tf.random_normal_initializer(stddev=1.0 / math.sqrt(1000)))
    b1 = tf.get_variable(name='FF-b1', shape=(100))
    l2 = tf.get_variable(name='FF-l2', shape=(100,2), 
         initializer=tf.random_normal_initializer(stddev=1.0 / math.sqrt(100)))
    b2 = tf.get_variable(name='FF-b2', shape=(2))
    logits = tf.matmul(tf.matmul(tf.matmul(inputs, l0) + b0, l1) + b1, l2) + b2
    cost = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(logits, targets))
    return cost


  # https://github.com/tensorflow/tensorflow/blob/r0.11/tensorflow/models/image/cifar10/cifar10_multi_gpu_train.py#L110
  def average_gradients(self, tower_grads):
    """Calculate the average gradient for each shared variable across all towers.
    Note that this function provides a synchronization point across all towers.
    Args:
      tower_grads: List of lists of (gradient, variable) tuples. The outer list
        is over individual gradients. The inner list is over the gradient
        calculation for each tower.
    Returns:
       List of pairs of (gradient, variable) where the gradient has been averaged
       across all towers.
    """
    average_grads = []
    for grad_and_vars in zip(*tower_grads):
      if grad_and_vars[0][0] != None:
        # Note that each grad_and_vars looks like the following:
        #   ((grad0_gpu0, var0_gpu0), ... , (grad0_gpuN, var0_gpuN))
        grads = []
        for g, _ in grad_and_vars:
          # Add 0 dimension to the gradients to represent the tower.
          expanded_g = tf.expand_dims(g, 0)
          
          # Append on a 'tower' dimension which we will average over below.
          grads.append(expanded_g)
        
        # Average over the 'tower' dimension.
        grad = tf.concat(0, grads)
        grad = tf.reduce_mean(grad, 0)
        
        # Keep in mind that the Variables are redundant because they are shared
        # across towers. So .. we will just return the first tower's pointer to
        # the Variable.
        v = grad_and_vars[0][1]
        grad_and_var = (grad, v)
        average_grads.append(grad_and_var)
    return average_grads


  def __init__(self, gpu_list, max_length):
    self.gpu_list = gpu_list
    self.max_length = max_length
    ## Create the model
    inputs = []
    targets = []
    costs = []
    tower_grads = []
    self.optimizer = tf.train.AdamOptimizer()
    for gpu in self.gpu_list:
      with tf.device('/gpu:%d' % gpu):
        with tf.name_scope('gpu_%d' % gpu) as scope:
          inp = tf.placeholder(tf.float32, shape=(None, self.max_length), name='source')
          tar = tf.placeholder(tf.float32, shape=(None, 2), name='target')
          c = self.createModel(inp, tar)
          tf.get_variable_scope().reuse_variables()
          tower_grads.append(self.optimizer.compute_gradients(c))
          inputs.append(inp)
          targets.append(tar)
          costs.append(c)

    self.inputs = tuple(inputs)
    self.targets = tuple(targets)

    ## Average gradients
    grads = self.average_gradients(tower_grads)
    self.train_op = self.optimizer.apply_gradients(grads)
    self.sess = tf.Session(config=tf.ConfigProto(allow_soft_placement=True))
    self.cost = sum(costs)/len(costs)

    ## Tensorboard
    self.train_cost_summary = tf.scalar_summary('train_cost', self.cost)
    self.writer = tf.train.SummaryWriter('events/OneGPU')
    self.sess.run(tf.initialize_all_variables())

  def train(self):
    for step in range(100000):
      inp = []
      tar = []
      for gpu in self.gpu_list:
        i,t = get_batch()
        inp.append(i)
        tar.append(t)
      feed_dict = {self.inputs: inp, self.targets: tar}
      cost_summary, _, cost = self.sess.run([self.train_cost_summary, self.train_op, self.cost], feed_dict)
      self.writer.add_summary(cost_summary, step)
      if step%1000 == 0:
        print step,"\t",cost


start = datetime.datetime.now()
print start
model = Model(gpu_list, max_length)
model.train()
end = datetime.datetime.now()
print "Total time: ", end - start
