import os
import joblib
import pickle
import cv2
import pandas as pd
import numpy as np

from sklearn.model_selection import KFold
from sklearn.preprocessing import Normalizer, LabelEncoder
from sklearn.svm import SVC
# from sklearn.neural_network import MLPClassifier
from sklearn.metrics import accuracy_score, classification_report

from face_embedding import get_faces_embedding

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR = os.path.join(PROJECT_DIR, 'models')
FILES_DIR = os.path.join(PROJECT_DIR, 'files')


class FaceRecognizer:
    def __init__(self, recognition_type):
        self._recognition_type = recognition_type
        self.recognizer = SuppVecMachinesRecognizer() if self._recognition_type == 'svm' else BaseRecognizer()
        self.labels = self.recognizer.labels

    def face_classification(self, face, embedding_model):
        if self._recognition_type == 'base':
            return self.recognizer.predict(face)
        elif self._recognition_type == 'svm':
            return self.recognizer.predict(face, embedding_model)


class BaseRecognizer:
    def __init__(self):
        self._recognizer = cv2.face.LBPHFaceRecognizer_create()
        self._trained_file_path = os.path.join(FILES_DIR, "recognize_trained.yml")
        self._labels_path = os.path.join(FILES_DIR, "labels.pickle")
        if os.path.exists(self._trained_file_path):
            self._recognizer.read(self._trained_file_path)
        self.labels = list(self.get_labels().values())

    def train_clf(self, data, labels):
        self._recognizer.train(data, np.asarray(labels))
        self._recognizer.save(self._trained_file_path)

    def predict(self, roi):
        gray_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        face_id, conf = self._recognizer.predict(gray_roi)
        return self.labels[face_id], conf

    def get_labels(self):
        with open(self._labels_path, 'rb') as file:
            labels = pickle.load(file)
            labels = {id_: label for label, id_ in labels.items()}
            return labels


class SuppVecMachinesRecognizer:
    def __init__(self):
        self._min_avg_acc = 0.7
        self._models_path = MODELS_DIR
        self._model = 'SVM_model.pkl'
        self.data_encoder = Normalizer(norm='l2')
        try:
            self._clf = joblib.load(os.path.join(self._models_path, self._model))
            self.label_encoder = joblib.load(os.path.join(MODELS_DIR, "label_encoder.pkl"))
        except FileNotFoundError:
            self._clf = SVC(gamma=0.001, kernel='linear', probability=True)
            self.label_encoder = LabelEncoder()
        self.labels = self.label_encoder.classes_

    def test_clf(self, X, y, stats, cv_=KFold(n_splits=10, shuffle=True, random_state=42)):
        scores, y_trues, y_predicts = [], [], []
        for train_idx, test_idx in cv_.split(X, y):
            X_train, X_test = X[train_idx], X[test_idx]
            y_train, y_test = y[train_idx], y[test_idx]

            self._clf.fit(X_train, y_train)
            y_predict = self._clf.predict(X_test)
            score = accuracy_score(y_test, y_predict)
            scores.append(score)
            y_trues.extend(self.label_encoder.inverse_transform(y_test))
            y_predicts.extend(self.label_encoder.inverse_transform(y_predict))
            # print(score*100)
        if stats:
            print(f'Avg score from {len(y)} samples is: {np.average(np.array(scores)) * 100:.2f}%')
            print(f'{pd.DataFrame(classification_report(y_trues, y_predicts, output_dict=True))}')
        return np.average(np.array(scores))

    def train_clf(self, X, y, show_stats=False):
        if self.test_clf(X, y, show_stats) > self._min_avg_acc:
            self._clf.fit(X, y)
            joblib.dump(self._clf, os.path.join(self._models_path, self._model))
        else:
            print(f"Cannot create model because average accuracy is under {self._min_avg_acc * 100:.2f}%")

    def predict(self, face, embedding_model):
        def transform_shape(_face):
            try:
                transformed_face = cv2.resize(_face, (160, 160))
                return transformed_face.reshape((1,) + transformed_face.shape)
            except:
                print('Something wrong')

        face = transform_shape(face)
        faces_embedding_ = get_faces_embedding(face, embedding_model)
        faces_embedding_encode_ = self.data_encoder.transform(faces_embedding_)
        self._clf = joblib.load(os.path.join(self._models_path, self._model))
        predict_class_ = self._clf.predict(faces_embedding_encode_)
        predict_prob_ = self._clf.predict_proba(faces_embedding_encode_)
        class_probability = predict_prob_[0, predict_class_[0]]
        predict_names = self.label_encoder.inverse_transform(predict_class_)
        print(f'Predicted: {predict_names[0]} - {class_probability * 100:.2f}%')
        return predict_names[0], class_probability*100
