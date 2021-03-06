import numpy as np
import tensorflow as tf

from tensorflow.contrib import learn
from tensorflow.contrib.learn.python.learn.estimators import model_fn as model_fn_lib
tf.logging.set_verbosity(tf.logging.INFO)

__author__ = "Sreejith Sreekumar"
__email__ = "sreekumar.s@husky.neu.edu"
__version__ = "0.0.1"


# 1. Convolution
# 2. Pooling
# 3. Convolution
# 4. Pooling
# 5. Dense


def cnn_model_function(features, labels, mode):

    # Input layer
    # [batch_size, image_width, image_height, channels]
    input_layer = tf.reshape(features, [-1, 28, 28, 1])

    # Convolution 1
    conv1 = tf.layers.conv2d(
      inputs=input_layer,
      filters=32,
      kernel_size=[5, 5],
      padding="same",
      activation=tf.nn.relu)

    # output tensor produced by conv2d() has a
    # shape of [batch_size, 28, 28, 32] - same dimensions
    # but 32 channels
    # pooling layer
    pool1 = tf.layers.max_pooling2d(inputs=conv1, pool_size=[2, 2], strides=2)

    # output from max pooling layer has a dimension of [batch_size, 14, 14, 32]
    # there is 50% reduction in the number of outputs from the filter
    conv2 = tf.layers.conv2d(
      inputs=pool1,
      filters=64,
      kernel_size=[5, 5],
      padding="same",
      activation=tf.nn.relu)

    # output from conv2 layer [batch_size, 14,14, 64] -  64 layers
    pool2 = tf.layers.max_pooling2d(inputs=conv2, pool_size=[2, 2], strides=2)

    # output from pool2 layer has dimensions [batch_size, 7, 7, 64]
    # before applying to dense layer we need to reshape it so that the
    # outputs are in two dimensions
    pool2_flat = tf.reshape(pool2, [-1, 7 * 7 * 64])

    dense = tf.layers.dense(inputs=pool2_flat,
                            units=1024, activation=tf.nn.relu)

    dropout = tf.layers.dropout(inputs=dense,
                                rate=0.4,
                                training=mode == learn.ModeKeys.TRAIN)
    logits = tf.layers.dense(inputs=dropout, units=10)

    # Cross entropy is the loss function we use for classification problems
    loss = None
    train_op = None

    if mode != learn.ModeKeys.INFER:
        onehot_labels = tf.one_hot(indices=tf.cast(labels, tf.int32), depth=10)
        loss = tf.losses.softmax_cross_entropy(onehot_labels=onehot_labels, logits=logits)

    if mode == learn.ModeKeys.TRAIN:
        train_op = tf.contrib.layers.optimize_loss(
            loss=loss,
            global_step=tf.contrib.framework.get_global_step(),
            learning_rate=0.001,
            optimizer="SGD")
    # tf.argmax(input=logits, axis=1)
    # tf.nn.softmax(logits, name="softmax_tensor")
    predictions = {
        "classes": tf.argmax(input=logits, axis=1),
        "probabilities": tf.nn.softmax(logits, name="softmax_tensor")
        }

    return model_fn_lib.ModelFnOps(mode=mode,
                                   predictions=predictions,
                                   loss=loss, train_op=train_op)


# classifying with MNIST classifier
mnist = learn.datasets.load_dataset("mnist")
train_data = mnist.train.images # Returns np.array
train_labels = np.asarray(mnist.train.labels, dtype=np.int32)
eval_data = mnist.test.images # Returns np.array
eval_labels = np.asarray(mnist.test.labels, dtype=np.int32)

# Create the Estimator
mnist_classifier = learn.Estimator(
      model_fn=cnn_model_function, model_dir="/tmp/mnist_convnet_model")

# Set up logging for predictions
tensors_to_log = {"probabilities": "softmax_tensor"}
logging_hook = tf.train.LoggingTensorHook(
  tensors=tensors_to_log, every_n_iter=50)


mnist_classifier.fit(
    x=train_data,
    y=train_labels,
    batch_size=100,
    steps=20000,
    monitors=[logging_hook])

metrics = {
    "accuracy":
        learn.MetricSpec(
            metric_fn=tf.metrics.accuracy, prediction_key="classes"),
}

eval_results = mnist_classifier.evaluate(
    x=eval_data, y=eval_labels, metrics=metrics)
print(eval_results)
