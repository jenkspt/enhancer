import numpy as np
from keras import backend as K
import tensorflow as tf
import cv2

def make_kernel(a):
	"""Transform a 2D array into a convolution kernel"""
	a = np.asarray(a)
	a = a.reshape(list(a.shape) + [1,1])
	return tf.constant(a, dtype=1)

laplace_k = make_kernel([[0.5, 1.0, 0.5],
					   [1.0, -6., 1.0],
					   [0.5, 1.0, 0.5]])

def simple_conv(x, k):
	"""A simplified 2D convolution operation"""
	# x = tf.expand_dims(tf.expand_dims(x, 0), -1)
	y = tf.nn.depthwise_conv2d(x, k, [1, 1, 1, 1], padding='SAME')
	# return y[0, :, :, 0]
	return y


def laplace(x):
	"""Compute the 2D laplacian of an array"""
	return simple_conv(x, laplace_k)


def gradient_importance(y_true, y_pred):
	importance = tf.abs(laplace(y_true))
	return K.mean(tf.mul(tf.abs(y_pred - y_true), tf.log(2 + importance)), axis=-1)
