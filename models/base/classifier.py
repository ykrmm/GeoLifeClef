import numpy as np

from sklearn.base import BaseEstimator, ClassifierMixin

# Scikit-learn validation tools
from sklearn.utils.validation import check_X_y, check_array, check_is_fitted
from sklearn.utils.multiclass import unique_labels

class Classifier(BaseEstimator, ClassifierMixin):

    """Generic abstract class for a classifier
       All classifiers defined must inherit from this class
       The class is a specialized estimator class from Scikit-learn, but
       adapted to a multilabel ranking problem.
       This way we can do a grid search, or random search on parameters or build
       a pipeline.
    """
    def __init__(self):
        """A classifier may have a Scikit-learn classifier as an attribute
           If so, methods fit and predict are already implemented here
           Else, they should be re-implemented
        """
    def fit(self, X, y, *args, **kwargs):
        """Trains the model on the dataset
           :param X: the training examples
           :param y: the training examples' labels
        """
        # check that X and y have correct shape
        X, y = check_X_y(X, y)

        if hasattr(self, 'clf'):
            self.clf.fit(X, y, *args, **kwargs)
            self.classes_ = self.clf.classes_

        self.X_ = X # training data
        self.y_ = y # training labels
        # the labels existing in the training set
        if not hasattr(self, 'classes_'):
            self.classes_ = unique_labels(y)

        return self

    def predict(self, X, return_proba=False, *args, **kwargs):
        """Predict the list of labels most likely to be observed
           for the data points given
        """
        if not (hasattr(self, 'clf')):
            raise NotImplementedError("No predict Scikit-learn estimator attribute "
                                       "the predict method should be implemented")

        if not hasattr(self.clf, 'predict_proba'):
            raise NotImplementedError("The Scikit-learn estimator does not have "
                                       "a predict_proba method, the predict method "
                                       "should be implemented")
        # check is fit had been called
        check_is_fitted(self, ['X_', 'y_'])
        # input validation
        X = check_array(X)

        # predict probabilities of labels for each examples
        probas = self.clf.predict_proba(X, *args, **kwargs)
        # get the indexes of the sorted probabilities, in decreasing order
        top_predictions = np.flip(np.argsort(probas, axis=1)[:,-self.ranking_size:],axis=1)

        # get the names of the classes predicted
        y_predicted = self.classes_[top_predictions]
        if return_proba:
            # get as well the probabilities of the predictions
            y_predicted_probas = [probas[i,pred] for i,pred in enumerate(top_predictions)]
            return np.array(y_predicted), np.array(y_predicted_probas)

        return np.array(y_predicted)


    # Here are metrics for model evaluation, which can be used to find best
    # parameters in a grid search. From most to less permissive, the metrics are
    # Top30, MRR and accuracy.

    def mrr_score(self, y_true, y_pred):

        """Computes the mean reciprocal rank :
           calculates the inverse of the rank of the true label among the
           predicted labels for every row, and computes the mean.

           :param y_pred: the predicted labels
           :param y_true: the true labels
           :return: the mean reciprocal rank, which ranges from 0
            null prediction) to 1 (perfect prediction)
        """
        score = 0.
        for idx,y in enumerate(y_pred):
            try:
                rank = np.where(y == y_true[idx])[0][0]
                score += 1./(rank+1)
            except IndexError: # the true specie is not predicted: scores zero
                pass

        return 1./len(y_pred) * score

    def top30_score(self, y_true, y_pred):

        """It is the accuracy based on the first 30 answers:
           The mean of the function scoring 1 when the good species is in the 30
           first answers, and 0 otherwise.

           :param y_pred: the predicted labels
           :param y_true: the true labels
           :return: the Top30 score, which ranges from 0
               (null prediction) to 1 (perfect prediction)
        """
        score = 0.
        for idx,y in enumerate(y_pred):
            try:
                rank = np.where(y[:min(30,len(y_pred))] == y_true[idx])[0][0]
                score += 1.
            except IndexError: # the true specie is not predicted: scores zero
                pass

        return 1./len(y_pred)* score

    def accuracy_score(self, y_true, y_pred):

        """Accuracy score:
           Mean of the function scoring 1 when the first predicted specie is
           the true specie. Very harsh metric.
        """
        return (y_pred[:,0] == y_true).mean()

    # def score(self, X, y, *args, **kwargs):

    #     """Score function used in cross-validation search. This is the Top30 metric.
    #     """
    #     return self.top30_score(self.predict(X, *args,**kwargs), y)

    def score(self, X, y):
        """Score function used in cross-validation search. This is the Top30 metric.
        """
        return self.top30_score(y, self.predict(X))

    # Below are other indicators of the performance or confidence of the model.

    def mean_rank_score(self, y_true, y_pred):

        """Computes the mean rank: the mean of the rank from the predicted labels
           that are present in the ranking.
           Predicted labels not present in the ranking are ignored.
        """
        score = 0.
        n_predicted = 0
        for idx,y in enumerate(y_pred):
            try:
                rank = np.where(y == y_true[idx])[0][0]
                score += rank+1
                n_predicted += 1
            except IndexError:
                pass
        if n_predicted == 0:
            return 'no'
        return 1./n_predicted * score

    def mean_sum_proba_rank(self, proba_pred):

        """"Mean of the sum of the probas of predicted labels by ranking.
            This measures the confidence in the prediction of the model: the higher
            a proba sum is in a label ranking, the more confident the model is
            in the choice he gives. Perfect confidence is a sum of 1.

            However this measure is not a performance metric. But it is likely
            that if a model has bad scores, it can be explained by low predicted
            probas.
        """
        return proba_pred.sum(axis=1).mean()


    def cross_validation(self, X, y, n_folds=5, shuffle=True, evaluation_metric='top30'):
        """Cross validation prodedure to evaluate the classifier
           :param X: the data used for training/validating
           :param y: the labels of the training data
           :param n_folds: the number of folds for the cross validation
           :param shuffle: whether or not to shuffle the dataset first
           :evaluation_metric: the evaluation metric function
           :return: the mean of the metric over the set of folds
        """
        # WE DON'T USE THIS
        # We use basic train-test split to evaluate or models as a first approach
        # We will then use CV for searching the best parameters via random search
        pass

    def random_search_cv(self, X_test, n_cv=5, n_folds_cv=5, evaluation_metric='top30'):
        """Random search for optimal hyperparameters

        """
        # DON'T KNOW IF WE WILL IMPLEMENT IT
        # We may implement a method on a per-classifier bases
        # depending on if the classifier is based on a Scikit-learn classifier
        # or not
        pass
