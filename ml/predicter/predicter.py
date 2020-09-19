# coding=utf-8

import math

import numpy as np
from sklearn.metrics import accuracy_score
from sklearn.svm import SVR

# import rtlearner as rtl
from dataaccess import dao
from utilities import util

# import matplotlib.pyplot as plt


clf = {'engin': None}


def build_model(data):
    classifiers = [
        SVR(kernel='rbf', C=1e3, gamma=0.1),
        SVR(kernel='linear', C=1e3),
        SVR(kernel='poly', C=1e3, degree=2)
        #     KNeighborsClassifier(3)
        # ,
        #    SVC(kernel="linear", C=0.025)
        # ,
        #    SVC(gamma=2, C=1)
        # ,
        # GaussianProcessClassifier(1.0 * RBF(1.0))
        # ,
        # DecisionTreeClassifier(
        #     class_weight=None, criterion='entropy', max_depth=8,
        #     max_features=None, max_leaf_nodes=None,
        #     min_samples_leaf=1,
        #     min_samples_split=2, min_weight_fraction_leaf=0.0,
        #     presort=False, random_state=10, splitter='best'
        # )
        # ,
        #  RandomForestClassifier(max_depth=20, n_estimators=20, max_features=1, criterion='entropy')
        # ,
        #  MLPClassifier(alpha=1)
        # ,
        #  AdaBoostClassifier()
        # ,
        #   GaussianNB()
        ,
        # QuadraticDiscriminantAnalysis(),
        # LogisticRegression(),
        # SVC(kernel='rbf', C=1000, gamma=0.001, probability=True),
        # DecisionTreeClassifier(),
        # RandomForestClassifier(max_depth=20, n_estimators=20, max_features=1, criterion='gini')
        # ,
        # GradientBoostingClassifier(random_state=1, n_estimators=20, learning_rate=0.1,
        #                               min_samples_leaf=1, min_samples_split=2, max_depth=8),
        # AdaBoostClassifier(n_estimators=10, algorithm='SAMME', base_estimator=RidgeClassifierCV(),
        #                       learning_rate=0.5),
        # BaggingClassifier(n_estimators=10, base_estimator=KNeighborsClassifier(n_neighbors=5))
    ]

    for clf in classifiers:
        print("-----------------------------")
        print(clf)
        print("-----------------------------")

        score = []
        maximum_score = 0
        for i in range(10):
            for ii in range(10):
                # compute how much of the data is training and testing
                data = np.random.permutation(data)
                # compute how much of the data is training and testing
                train_rows = int(math.floor(0.6 * data.shape[0]))

                # separate out training and testing data
                x_train = data[:train_rows, 1:]
                y_train = data[:train_rows, :1]
                x_test = data[train_rows:, 1:]
                y_test = data[train_rows:, :1]

                # Fit regression model
                clf.fit(x_train, y_train.ravel())
                # Predict out of sample
                y_predicted = clf.predict(x_test)
                # score.append(accuracy_score((y_test, y_predicted) * 100)
                if accuracy_score(y_test, y_predicted) > maximum_score:
                    maximum_score = accuracy_score(y_test, y_predicted)
                    best_clf = clf
            print("Number of runs", ii)
            # print "Socre mean", np.array(score).mean()
            print("Max ", maximum_score)
            # file = open(model_name+"_"+str(math.floor(100*maximum_score)), "w")
            # pickle.dump(best_clf, file)
            # file.close()
        return clf


def get_ads_dataset(filters, fields_to_project, target_field):
    db = dao.get_db()
    try:
        # {
        #     "brand": ObjectId("5916d82fff4a4215c6cb2ac7"),
        #     "model": ""
        #     "year": "٢٠١٥",
        #     "body_type": "",
        #     "engine": 0,
        #     "power": 0,
        #     "fuel": "",
        #     "transmission": "اوتوماتيك",
        #     "location": "جدة",
        #     "specs": ""
        # }

        # {"body_type": {"$ne": ""}, "$and": [{"engine": {"$ne": "0"}}, {"engine": {"$ne": 0}}],
        #  "power": {"$ne": 0}, "fuel": {"$ne": ""}, "specs": {"$ne": ""}},
        # {"brand": 1, "model": 1, "year": 1, "body_type": 1, "engine": 1, "power": 1, "fuel": 1,
        #  "transmission": 1, "location": 1, "specs": 1, "_id": 0}):

        ads = []
        for ad in db.products.find(filters,
                                   {"brand": 1, "model": 1, "year": 1, "body_type": 1, "engine": 1, "power": 1,
                                    "fuel": 1,
                                    "transmission": 1, "location": 1, "specs": 1, "_id": 0}):
            temp = []
            target_field_index = 0
            counter = -1
            for key in ad:
                if key in fields_to_project:
                    if key != target_field:
                        temp.append(hash(ad[key]))
                    else:
                        temp.append(ad[key])
                    counter += 1
                if key == target_field:
                    target_field_index = counter
            ads.append(temp)
        ads = np.array(ads)

        # swapping columns so that y i.e target is col 0
        ads[:, 0], ads[:, target_field_index] = ads[:, target_field_index], ads[:, 0].copy()

        # # cleaning engine capcity less than 1000 cc
        # ads[ads[:, 0] > 900, :]

        # # lebeling rest of columns
        # le = preprocessing.LabelEncoder()
        # for i in range (1,ads.shape[1]):
        #      le.fit(ads[:,i])
        #      ads[:, i] = le.fit_transform(ads[:,i])

        # Calculate mode of each column except target key
        # max(set(list), key=list.count)

        return ads
    except (Exception, e):
        util.logerr(str(e))
    return


def prepare_ad_to_query(ad, fields_to_project):
    try:
        ad_ = []
        temp = []
        for key in ad[0]:
            if key in fields_to_project:
                temp.append(hash(ad[0][key]))
        ad_.append(temp)
        ad_ = np.array(ad_)

        # # lebeling rest of columns
        # for i in range (ad_.shape[1]):
        #      ad_[:, i] = le.transform(ad_[:,i])

        return ad_
    except (Exception, e):
        util.logerr(str(e))
    return


def build_engin_prediction_model():
    ads = get_ads_dataset({"$and": [{"engine": {"$ne": "0"}}, {"engine": {"$ne": 0}}]},
                          ["brand", "model", "engine"], "engine")
    return build_model(ads)


def build_power_prediction_model():
    util.loginfo("==============================================================")

    ads = get_ads_dataset({"$and": [{"engine": {"$ne": "0"}}, {"engine": {"$ne": 0}}],
                           "$and": [{"power": {"$ne": 0}}, {"power": {"$ne": "0"}}]},
                          ["model", "engine", "power"], "power")

    build_model(ads, "power")
    util.loginfo("======================== Done ===============================")


def build_specs_prediction_model():
    util.loginfo("==============================================================")
    ads = get_ads_dataset({"body_type": {"$ne": ""}, "$and": [{"engine": {"$ne": "0"}}, {"engine": {"$ne": 0}}],
                           "$and": [{"power": {"$ne": 0}}, {"power": {"$ne": "0"}}], "fuel": {"$ne": ""},
                           "specs": {"$ne": ""}},
                          ["brand", "model", "engine", "power", "body_type", "fuel", "price", "specs"], "specs")
    build_model(ads, "specs")
    util.loginfo("======================== Done ===============================")


def build_price_prediction_model():
    util.loginfo("==============================================================")
    ads = get_ads_dataset({"body_type": {"$ne": ""}, "fuel": {"$ne": ""}, "price": {"$ne": ""}, "color": {"$ne": ""},
                           "year": {"$ne": ""}, "mileage": {"$ne": ""}},
                          ["brand", "model", "year", "body_type", "transmission", "location", "specs", "color",
                           "mileage"], "price")
    build_model(ads, "price")
    util.loginfo("======================== Done ===============================")


def query_engin_prediction_model(ad_to_predict):
    if clf['engin'] == None:
        clf['engin'] = build_engin_prediction_model()

    ad = prepare_ad_to_query(ad_to_predict, ["brand", "model"])
    return clf['engin'].predict(ad)


def main():
    util.loginfo("==============================================================")


if __name__ == '__main__':
    main()
