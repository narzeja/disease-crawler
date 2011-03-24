#!/usr/bin/env python

import numpy
import math
import hcluster.distance as hdist

class kNN:
    """
    classes  List of the possible classes.
    xs       List of the neighbors.
    ys       List of the classes that the neighbors belong to.
    k        Number of neighbors to look at.

    """
    def __init__(self):
        self.classes = []
        self.xs = []
        self.ys = []
        self.k = None

def equal_weight(x, y):
    """equal_weight(x, y) -> 1"""
    # everything gets 1 vote
    return 1

def train(xs, ys, k, typecode=None):
    """train(xs, ys, k) -> kNN

    Train a k nearest neighbors classifier on a training set.  xs is a
    list of observations and ys is a list of the class assignments.
    Thus, xs and ys should contain the same number of elements.  k is
    the number of neighbors that should be examined when doing the
    classification.

    """
    knn = kNN()
    knn.classes = set(ys)
    knn.xs = numpy.asarray(xs, typecode)
    knn.ys = ys
    knn.k = k
    return knn


def euclidian(x,y):
    d = x-y
    return numpy.sqrt(numpy.dot(d,d))

def calculate(knn, x, weight_fn=equal_weight, distance_fn=hdist.euclidian):
    """calculate(knn, x[, weight_fn][, distance_fn]) -> weight dict

    Calculate the probability for each class.  knn is a kNN object.  x
    is the observed data.  weight_fn is an optional function that
    takes x and a training example, and returns a weight.  distance_fn
    is an optional function that takes two points and returns the
    distance between them.  If distance_fn is None (the default), the
    Euclidean distance is used.  Returns a dictionary of the class to
    the weight given to the class.

    """
    x = numpy.asarray(x)
    order = []  # list of (distance, index)
    for i in range(len(knn.xs)):
#            temp[:] = x - knn.xs[i]
#            dist = numpy.sqrt(numpy.dot(temp,temp))
        dist = distance_fn(x, knn.xs[i])
        order.append((dist, i))
    order.sort()

    # first 'k' are the ones I want.
    weights = {}  # class -> number of votes
    for k in knn.classes:
        weights[k] = 0.0
    for dist, i in order[:knn.k]:
        klass = knn.ys[i]
        weights[klass] = weights[klass] + weight_fn(x, knn.xs[i])

    return weights, order

def classify(knn, x, weight_fn=equal_weight, distance_fn=hdist.euclidian):
    """classify(knn, x[, weight_fn][, distance_fn]) -> class

    Classify an observation into a class.  If not specified, weight_fn will
    give all neighbors equal weight and distance_fn will be the euclidean
    distance.

    """
    weights,_ = calculate(knn, x, weight_fn, distance_fn)

    most_class = None
    most_weight = None
    for klass, weight in weights.items():
        if most_class is None or weight > most_weight:
            most_class = klass
            most_weight = weight
    return most_class

