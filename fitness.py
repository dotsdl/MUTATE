from __future__ import print_function
import tensorflow as tf

class Fitness(object):
    '''
    Fitness Function to evaluate the Phenome
    '''

    def __init__(self, data, PHENOME):
        self.data = data
        self.phenome = PHENOME

    def evaluate(self):
        X,Y = self.data
        x_,y_,op = self.phenome

        sess = tf.Session()

        result = sess.run(op, feed_dict={x_: X, y_: Y})
        error = sess.run(tf.sqrt(tf.reduce_mean(tf.square(tf.subtract(Y, result)))))

        if error >= 0.0001:
            solved = False
            return result,error,solved

        if error <= 0.0001:
            solved = True
            return result,error,solved
