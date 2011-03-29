#!/usr/bin/env python

import numpy
import hcluster.distance as hdist
import db as DB
import TextmineThis as TT
import pod as POD

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
        self.miner = TT.Textminer()
        self.db = DB.db()

    def precalc(self):
        data = POD.parseOrphaDesc()
        return self.miner.createTermDoc(data) # termdoc, t_hash, d_hash, n_hash

    def trainfromtfidf(self, termDoc, t_hash, d_hash, n_hash):
        codes=["A","C","D","E","F","G","H","I","J","K","L","M","N","O","P","Q","R","S","V","Z"]
        icd10 = self.db.c.execute("select patres,code from icd_10").fetchall()
        dicd10 = dict(icd10)
        patrescodes = d_hash.keys() # ({patres0, docIndex0}, {patres1, docIndex1}, etc.)
        notpatres = set(patrescodes).difference(set(dicd10.keys()))

        toclassifyidx = [(d_hash[code], code) for code in notpatres]
        totrainidx = [(d_hash[code], code) for code in patrescodes if code not in notpatres]

        #construct the training feature dictionary
        features = []
        for (idx, patcode) in totrainidx:
            features.append({"feat": termDoc[idx].tolist(), "class": dicd10[patcode][0]})

        return features, totrainidx, toclassifyidx


    def train(self, feats, k, typecode=None):
        """train(xs, ys, k) -> kNN

        Train a k nearest neighbors classifier on a training set.  xs is a
        list of observations and ys is a list of the class assignments.
        Thus, xs and ys should contain the same number of elements.  k is
        the number of neighbors that should be examined when doing the
        classification.

        """

        # x = {feat: [], class: ''}
        features = []
        featclass = []
        for feat in feats:
            features+=feat['feat']
            featclass+=feat['class']*len(feat['feat'])
        self.classes = set(featclass)
        self.xs = numpy.asarray(features, typecode)
        self.ys = featclass
        self.k = k


    def calculate(self, x, weight_fn=lambda x, y: 1, distance_fn=hdist.euclidean):
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
        for i in range(len(self.xs)):
    #            temp[:] = x - knn.xs[i]
    #            dist = numpy.sqrt(numpy.dot(temp,temp))
            dist = distance_fn(x, self.xs[i])
            order.append((dist, i))
        order.sort()

        # first 'k' are the ones I want.
        weights = {}  # class -> number of votes
        for k in self.classes:
            weights[k] = 0.0
        for dist, i in order[:self.k]:
            klass = self.ys[i]
            weights[klass] = weights[klass] + weight_fn(x, self.xs[i])

        return weights, order

    def classify(self, x, weight_fn=lambda x, y: 1, distance_fn=hdist.euclidean):
        """classify(knn, x[, weight_fn][, distance_fn]) -> class

        Classify an observation into a class.  If not specified, weight_fn will
        give all neighbors equal weight and distance_fn will be the euclidean
        distance.

        """
        weights,_ = self.calculate(x, weight_fn, distance_fn)

        most_class = None
        most_weight = None
        for klass, weight in weights.items():
            if most_class is None or weight > most_weight:
                most_class = klass
                most_weight = weight
        return most_class

