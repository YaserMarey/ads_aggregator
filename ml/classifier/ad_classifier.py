# coding=utf-8
#####################################################
# Running main starts training step
# Data is read from local database, products_training
# classify methods is used by readers prior to saving
# an ad to the database to calculated ad_cat.
# reader initilize classifier with model stored in
# ad_classifier_model.pickle, and uses stop words from
# ad_classifier_model_set.txt file
#####################################################
# coding=utf-8
import math
import pickle
import random
import re
import sys

import nltk.classify.decisiontree
import numpy as np
from nltk.classify import SklearnClassifier
from nltk.corpus import stopwords
from nltk.tokenize import RegexpTokenizer
from pymongo import MongoClient
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import MultinomialNB
from sklearn.svm import LinearSVC

from settings import settings
from utilities import util

reload(sys)
sys.setdefaultencoding('utf-8')

#############################################################################################################
from nltk.classify import ClassifierI


class VoteClassifier(ClassifierI):
    def __init__(self, classifier_list=[
        ('linear_svc_2', SklearnClassifier(LinearSVC())),
        ('log_reg_1_2', SklearnClassifier(LogisticRegression())),
        ('log_reg_2_2', SklearnClassifier(LogisticRegression())),
        ('log_reg_3_2', SklearnClassifier(LogisticRegression())),
        ('multinom_nb_1_2', SklearnClassifier(MultinomialNB())),
        ('multinom_nb_2_2', SklearnClassifier(MultinomialNB())),
        ('multinom_nb_3_2', SklearnClassifier(MultinomialNB())),
        ('linear_svc_3', SklearnClassifier(LinearSVC())),
        ('log_reg_1_3', SklearnClassifier(LogisticRegression())),
        ('log_reg_2_3', SklearnClassifier(LogisticRegression())),
        ('log_reg_3_3', SklearnClassifier(LogisticRegression())),
        ('multinom_nb_1_3', SklearnClassifier(MultinomialNB())),
        ('multinom_nb_2_3', SklearnClassifier(MultinomialNB())),
        ('multinom_nb_3_3', SklearnClassifier(MultinomialNB()))]):

        self.classifiers_list = []
        self.trained_classifiers = []
        self.words_sets = {}
        self.stop_words = []

        self.classifiers_list = classifier_list

        self.ad_cats = ['SAL', 'PRT', 'TRN', 'SVC', 'EXP', 'REQ', 'ACC', 'EXC', 'OTH', 'INV']

        if (self.checkIfModelsExist()):
            util.loginfo("---------------------- reading models ------------------------")
            self.read_models()
        else:
            util.loginfo("-------------- models not there, start training --------------")
            self.train()
            # self.extract_features()

    def read_models(self):
        self.trained_classifiers = []
        self.words_sets = {}
        for classifier_name, classifier in self.classifiers_list:
            f = open(settings[settings['ENVIRONMENT']]['ML_FOLDER_PATH'] +
                     'classifier/model/' + classifier_name + '.pickle', 'rb')

            classifier = pickle.load(f)
            f.close()
            self.trained_classifiers.append((classifier_name, classifier))

            f = open(settings[settings['ENVIRONMENT']]['ML_FOLDER_PATH'] +
                     'classifier/model/words_set_' + classifier_name + '.txt', 'r')

            word_set = f.readline().decode('utf-8').split(' ')
            f.close()

            self.words_sets[classifier_name] = word_set
        f = open(settings[settings['ENVIRONMENT']]['ML_FOLDER_PATH'] +
                 'classifier/model/stop_words_set.txt', 'r')
        self.stop_words = f.readline().decode('utf-8').split(' ')
        f.close()

    def checkIfModelsExist(self):
        import os.path
        util.loginfo("-------------- checking if models exist --------------")
        for classifier_name, classifier in self.classifiers_list:
            if os.path.isfile(settings[settings['ENVIRONMENT']]['ML_FOLDER_PATH'] +
                              'classifier/model/' + classifier_name + '.pickle') == False:
                return False

            if os.path.isfile(settings[settings['ENVIRONMENT']]['ML_FOLDER_PATH'] +
                              'classifier/model/words_set_' + classifier_name + '.txt') == False:
                return False

        if os.path.isfile(settings[settings['ENVIRONMENT']]['ML_FOLDER_PATH'] +
                          'classifier/model/stop_words_set.txt') == False:
            return False

        return True

    def train(self):
        # read ads samples from training database
        min_word_length = 2
        min_word_freq = 5
        no_training_rounds = 11
        all_stop_words = self.get_stopwords()

        raw_list_of_ads = self.read_data_from_db()

        raw_list_of_ads = [({'ad_text':
                                 ad['description']
                                 + " " + ad['title']
                                 + " " + (ad['source']).replace('.com', '').replace('.sa', '').replace('.ksa', '')
                                 + (" " + (ad['ad_page_link'][:-1]).rsplit('/', 1)[-1])
                                 if (ad['source'] == 'haraj.com.sa') else ""},
                            ad['ad_cat']) for ad in raw_list_of_ads]

        for (classifier_name, classifier) in self.classifiers_list:
            accuracy_ary = []
            best_accuracy = 0
            util.loginfo("----------------" + classifier_name + " training ----------------")
            for i in range(0, no_training_rounds):
                random.shuffle(raw_list_of_ads)
                raw_train_rows = int(math.floor(0.7 * len(raw_list_of_ads)))
                raw_train_set, raw_test_set = raw_list_of_ads[:raw_train_rows], raw_list_of_ads[raw_train_rows:]

                all_words_set = self.extract_word_set(raw_train_set, all_stop_words, min_word_length, min_word_freq)

                train_list_of_ads = [(self.generate_feature(ad, all_words_set), cat) for (ad, cat) in raw_train_set]
                test_list_of_ads = [(self.generate_feature(ad, all_words_set), cat) for (ad, cat) in raw_test_set]

                classifier = classifier.train(train_list_of_ads)

                accuracy = nltk.classify.accuracy(classifier, test_list_of_ads)

                if accuracy > best_accuracy:
                    best_accuracy = accuracy
                    best_classifier = classifier
                    best_words_set = all_words_set
                accuracy_ary.append(accuracy)
                util.loginfo("accuracy : " + str(accuracy))
            util.loginfo("average accuracy :" + str(np.average(accuracy_ary)))

            # best_classifier, best_words_set = self.feature_selection(5, raw_list_of_ads, best_classifier,
            #                                                          best_words_set, np.median(accuracy_ary))

            self.save_classifier_model(best_classifier, classifier_name)
            self.trained_classifiers.append((classifier_name, best_classifier))
            self.save_word_set(best_words_set, classifier_name)
            self.words_sets[classifier_name] = best_words_set
        self.save_stop_words_set(all_stop_words)
        self.stop_words = all_stop_words
        util.loginfo("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
        util.loginfo("voteclassifier accuracy is:" + str(nltk.classify.accuracy(self, test_list_of_ads)))
        util.loginfo("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
        util.logdebug("read models")
        self.read_models()
        util.loginfo("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
        util.loginfo("voteclassifier accuracy is:" + str(nltk.classify.accuracy(self, test_list_of_ads)))
        util.loginfo("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")

    def feature_selection(self, number_of_features_to_remove, raw_list_of_ads, best_classifier, best_words_set,
                          best_accuracy):
        # read ads samples from training database

        util.loginfo("---------------- feature selection ----------------")
        util.logdebug("accuracy trying to beat is " + str(best_accuracy))
        number_of_features_removed = 0
        counter = 0
        while counter < len(best_words_set) - 1 and number_of_features_removed < 3:
            removed = best_words_set.pop(random.randint(0, len(best_words_set) - 1))
            util.logdebug("feature trying to test its value is " + u''.join(removed))
            accuracy_ = []
            for i in range(0, 11):
                util.logdebug("shuffling for " + str(i))
                random.shuffle(raw_list_of_ads)
                raw_train_rows = int(math.floor(0.7 * len(raw_list_of_ads)))
                raw_train_set, raw_test_set = raw_list_of_ads[:raw_train_rows], raw_list_of_ads[raw_train_rows:]

                train_list_of_ads = [(self.generate_feature(ad, best_words_set), cat) for (ad, cat) in raw_train_set]
                test_list_of_ads = [(self.generate_feature(ad, best_words_set), cat) for (ad, cat) in raw_test_set]

                new_classifier = best_classifier.train(train_list_of_ads)

                new_accuracy = nltk.classify.accuracy(best_classifier, test_list_of_ads)

                # accuracy_.append(new_accuracy)
                # if new_accuracy > accuracy_:
                #     util.logdebug("found new local accuracy"  + str (new_accuracy))
                #     accuracy_ = new_accuracy
                accuracy_.append(new_accuracy)
            if np.median(accuracy_) > best_accuracy:
                util.loginfo("---------- accuracy captured when removing " + removed + " is " + str(accuracy_))
                util.loginfo("---------- new median accuracy" + str(np.median(accuracy_)))
                util.loginfo("---------- feature removed is" + u''.join(removed))
                best_accuracy = np.median(accuracy_)
                best_classifier = new_classifier
                number_of_features_removed += 1
            else:
                best_words_set.append(removed)
            if number_of_features_removed >= number_of_features_to_remove: break
            counter += 1
        util.loginfo("accuracy : " + str(best_accuracy))
        return best_classifier, best_words_set

    #     TODO incomplete trial for feature selection
    def extract_features(self):
        # read ads samples from training database
        min_word_length = 2
        min_word_freq = 5
        no_training_rounds = 5
        all_stop_words = self.get_stopwords()

        raw_list_of_ads = self.read_data_from_db()

        raw_list_of_ads = [({'ad_text':
                                 ad['description']
                                 + " " + ad['title']
                                 + " " + (ad['source']).replace('.com', '').replace('.sa', '').replace('.ksa', '')
                                 + (" " + (ad['ad_page_link'][:-1]).rsplit('/', 1)[-1])
                                 if (ad['source'] == 'haraj.com.sa') else ""},
                            ad['ad_cat']) for ad in raw_list_of_ads]

        for (classifier_name, classifier) in self.classifiers_list:
            accuracy_ary = []
            best_accuracy = 0
            util.loginfo("----------------" + classifier_name + " training ----------------")
            all_words_set = []
            for i in range(0, len(self.words_sets[classifier_name])):
                all_words_set = self.words_sets[classifier_name].pop(i)
                random.shuffle(raw_list_of_ads)
                raw_train_rows = int(math.floor(0.7 * len(raw_list_of_ads)))
                raw_train_set, raw_test_set = raw_list_of_ads[:raw_train_rows], raw_list_of_ads[raw_train_rows:]
                train_list_of_ads = [(self.generate_feature(ad, all_words_set), cat) for (ad, cat) in raw_train_set]
                test_list_of_ads = [(self.generate_feature(ad, all_words_set), cat) for (ad, cat) in raw_test_set]

                classifier = classifier.train(train_list_of_ads)

                accuracy = nltk.classify.accuracy(classifier, test_list_of_ads)

                if accuracy > best_accuracy:
                    util.log("found new best accuracy" + str(accuracy))
                    best_accuracy = accuracy
                    best_classifier = classifier
                    best_words_set = all_words_set
                    self.words_sets[classifier_name] = all_words_set

            util.loginfo("best accuracy : " + str(best_accuracy))

            self.save_classifier_model(best_classifier, classifier_name)
            self.trained_classifiers.append((classifier_name, best_classifier))
            self.save_word_set(best_words_set, classifier_name)
            self.words_sets[classifier_name] = best_words_set

        # self.save_stop_words_set(all_stop_words)
        # self.stop_words = all_stop_words
        util.loginfo("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
        util.loginfo("voteclassifier accuracy is:" + str(nltk.classify.accuracy(self, test_list_of_ads)))
        util.loginfo("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
        util.logdebug("read models")
        self.read_models()
        util.loginfo("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
        util.loginfo("voteclassifier accuracy is:" + str(nltk.classify.accuracy(self, test_list_of_ads)))
        util.loginfo("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")

    def classify(self, ad, is_raw_ad=False):

        votes = {'SAL': 0, 'PRT': 0, 'TRN': 0, 'SVC': 0, 'EXP': 0, 'REQ': 0, 'ACC': 0, 'EXC': 0, 'OTH': 0, 'INV': 0}

        if is_raw_ad:
            ad = ({'ad_text': ad['description']
                              + " " + ad['title']
                              + " " + (ad['source']).replace('.com', '').replace('.sa', '').replace('.ksa', '')
                              + (" " + (ad['ad_page_link'][:-1]).rsplit('/', 1)[-1])
            if (ad['source'] == 'haraj.com.sa') else ""})
            util.logdebug("-------------------------------------------------------------------------")
            util.logdebug(ad['ad_text'])
            util.logdebug("-------------------------------------------------------------------------")
        else:
            ad_txt = ''
            for w in ad:
                if ad[w] == True: ad_txt += ' ' + w
            print(ad_txt)

        for classifier_name, classifier in self.trained_classifiers:
            if is_raw_ad:
                vote = classifier.classify(self.generate_feature(ad, self.words_sets[classifier_name]))
            else:
                vote = classifier.classify(ad)

            if vote == '': continue
            util.logdebug(classifier_name + " votted :" + vote)
            votes[vote] += 1
        util.logdebug("final votes for all overall classifiers for all cats" + str(votes))

        vote = max(votes, key=votes.get)
        confidence = float(votes[max(votes, key=votes.get)]) / float(len(self.trained_classifiers))
        util.loginfo("final vote is :" + vote)
        util.loginfo("confidenc is :" + str(confidence))
        if is_raw_ad:
            return vote, confidence
        else:
            return vote

    # pick ads that are categorized i.e prepared for training from the products_training
    def read_data_from_db(self):
        db = MongoClient()['materialshop-dev']
        return list(db.products_training.find({'ad_cat': {'$exists': True}}))

    # stop words are read from a file, this file I picked from the internet, possibly not the best thing
    def get_stopwords(self):
        stop_words = []
        f = open(settings[settings['ENVIRONMENT']]['ML_FOLDER_PATH'] + 'classifier/arabic_stop_words.txt', 'r')
        for item in f.read().split('\n'):
            stop_words.append(item)

        f = open(settings[settings['ENVIRONMENT']]['ML_FOLDER_PATH'] + 'classifier/ads_stop_words.txt', 'r')
        for item in f.read().split('\n'):
            stop_words.append(item)

        english_stop_words = set(stopwords.words("english"))
        arabic_stop_words = set(stopwords.words("arabic"))

        return set(stop_words).union(english_stop_words).union(arabic_stop_words)

    # tokneize, remove numbers
    def toknies_ads(sefl, list_of_ads):
        all_words_set = []
        tokenizer = RegexpTokenizer(r'\w+')
        for (ad, cat) in list_of_ads:
            all_words_set += tokenizer.tokenize((re.sub(r'\d+', '', ad['ad_text'])).lower())

        return all_words_set

    def extract_word_set(self, list_of_ads, all_stop_words, min_word_length, min_word_freq):

        all_words_set = self.toknies_ads(list_of_ads)

        dist = nltk.FreqDist(all_words_set)

        all_words_set = [w for (w, f) in dist.most_common()]
        all_words_set = [w for w in all_words_set if w not in all_stop_words]
        all_words_set = [w for w in all_words_set if len(w) > min_word_length]
        all_words_set = [w for w in all_words_set if dist[w] > min_word_freq]

        return all_words_set

    def generate_feature(self, ad, all_words_set):
        tokenizer = RegexpTokenizer(r'\w+')
        ad_words = set(tokenizer.tokenize((re.sub(r'\d+', '', ad['ad_text'])).lower()))
        features = {}
        for word in all_words_set:
            features[word] = (word in ad_words)
        return features

    def save_classifier_model(self, best_classifier, classifier_name):
        with open(settings[settings['ENVIRONMENT']]['ML_FOLDER_PATH'] +
                  '/classifier/model/' + classifier_name + '.pickle', 'wb') as f:
            pickle.dump(best_classifier, f)

    def save_word_set(self, all_words_set, classifier_name):
        f = open(
            settings[settings['ENVIRONMENT']]['ML_FOLDER_PATH'] +
            '/classifier/model/words_set_' + classifier_name + '.txt', 'w')
        f.write(u' '.join(all_words_set).encode('utf-8'))
        f.close()

    def save_stop_words_set(self, stop_words):
        f = open(settings[settings['ENVIRONMENT']]['ML_FOLDER_PATH'] +
                 '/classifier/model/stop_words_set.txt', 'w')
        f.write(u' '.join(stop_words).encode('utf-8'))
        f.close()


if __name__ == '__main__':
    # vote_classifer_1 = VoteClassifier( classifier_list=[
    #  ('linear_svc_1', SklearnClassifier(LinearSVC())),
    #  ('log_reg_1_1', SklearnClassifier(LogisticRegression())),
    #  ('log_reg_2_1', SklearnClassifier(LogisticRegression())),
    #  ('log_reg_3_1', SklearnClassifier(LogisticRegression())),
    #  ('multinom_nb_1_1', SklearnClassifier(MultinomialNB())),
    #  ('multinom_nb_2_1', SklearnClassifier(MultinomialNB())),
    #  ('multinom_nb_3_1', SklearnClassifier(MultinomialNB()))])

    vote_classifer_2 = VoteClassifier(classifier_list=[
        ('linear_svc_2', SklearnClassifier(LinearSVC())),
        ('log_reg_1_2', SklearnClassifier(LogisticRegression())),
        ('log_reg_2_2', SklearnClassifier(LogisticRegression())),
        ('log_reg_3_2', SklearnClassifier(LogisticRegression())),
        ('multinom_nb_1_2', SklearnClassifier(MultinomialNB())),
        ('multinom_nb_2_2', SklearnClassifier(MultinomialNB())),
        ('multinom_nb_3_2', SklearnClassifier(MultinomialNB())),
        ('linear_svc_3', SklearnClassifier(LinearSVC())),
        ('log_reg_1_3', SklearnClassifier(LogisticRegression())),
        ('log_reg_2_3', SklearnClassifier(LogisticRegression())),
        ('log_reg_3_3', SklearnClassifier(LogisticRegression())),
        ('multinom_nb_1_3', SklearnClassifier(MultinomialNB())),
        ('multinom_nb_2_3', SklearnClassifier(MultinomialNB())),
        ('multinom_nb_3_3', SklearnClassifier(MultinomialNB()))])

    # import matplotlib.pyplot as plt
    # lw = 2
    # plt.scatter(X, y, color='darkorange', label='data')
    # plt.plot(X, predicted, color='navy', lw=lw, label='RBF model')
    # plt.plot(X, y_lin, color='c', lw=lw, label='Linear model')
    # plt.plot(X, y_poly, color='cornflowerblue', lw=lw, label='Polynomial model')
    # plt.xlabel('data')
    # plt.ylabel('target')
    # plt.title('Support Vector Regression')
    # plt.legend()
    # plt.show()
