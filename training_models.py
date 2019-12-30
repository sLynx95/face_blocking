import pandas as pd

from sklearn.model_selection import KFold
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score

df = pd.read_json('data_from_images.json').values
y, X = df[:, 0], df[:, 1:]
print(df)

cv = KFold(n_splits=10, shuffle=True, random_state=42)
clf = SVC(gamma=0.001)

for train_idx, test_idx in cv.split(X, y):
    print("TRAIN:", train_idx, "TEST:", test_idx)
    X_train, X_test = X[train_idx], X[test_idx]
    y_train, y_test = y[train_idx], y[test_idx]

    # print(X_test)
    # clf.fit(X_train, y_train)
    # y_predict = clf.predict(X_test)
    # score = accuracy_score(y_test, y_predict)
    # print(score)

print(len(y))
