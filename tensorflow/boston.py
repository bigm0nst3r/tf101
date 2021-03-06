import matplotlib.pyplot as plt
import tensorflow as tf
import numpy as np

from numpy import genfromtxt
from sklearn.datasets import load_boston

# Source :: https://aqibsaeed.github.io/2016-07-07-TensorflowLR/


# Getting data from a csv
def read_dataset(filePath,  delimiter=', '):
    return genfromtxt(filePath,  delimiter=delimiter)


# Getting data from sklean
def read_boston_data():
    boston = load_boston()
    features = np.array(boston.data)
    labels = np.array(boston.target)
    return features,  labels


def feature_normalize(dataset):
    mu = np.mean(dataset,  axis=0)
    sigma = np.std(dataset,  axis=0)
    return (dataset - mu)/sigma


def append_bias_reshape(features,  labels):
    n_training_samples = features.shape[0]
    n_dim = features.shape[1]
    f = np.reshape(np.c_[np.ones(n_training_samples), features],
                       [n_training_samples, n_dim + 1])
    l = np.reshape(labels,  [n_training_samples,  1])
    return f,  l


features,  labels = read_boston_data()
normalized_features = feature_normalize(features)
f,  l = append_bias_reshape(normalized_features, labels)
n_dim = f.shape[1]

rnd_indices = np.random.rand(len(features)) < 0.80

train_x = f[rnd_indices]
train_y = l[rnd_indices]
test_x = f[~rnd_indices]
test_y = l[~rnd_indices]

learning_rate = 0.01
training_epochs = 1000
cost_history = np.empty(shape=[1], dtype=float)

X = tf.placeholder(tf.float32, [None, n_dim])
Y = tf.placeholder(tf.float32, [None, 1])
W = tf.Variable(tf.ones([n_dim, 1]))

init = tf.initialize_all_variables()

y_ = tf.matmul(X,  W)
cost = tf.reduce_mean(tf.square(y_ - Y))
training_step = tf.train.GradientDescentOptimizer(learning_rate).minimize(cost)


# initialize
sess = tf.Session()
sess.run(init)

for _ in range(training_epochs):
    sess.run(training_step, feed_dict={X: train_x, Y: train_y})
    cost_history = np.append(cost_history, sess.run(cost,
                                          feed_dict={X: train_x, Y: train_y}))

# plotting
plt.plot(range(len(cost_history)), cost_history)
plt.axis([0, training_epochs, 0, np.max(cost_history)])
plt.show()
