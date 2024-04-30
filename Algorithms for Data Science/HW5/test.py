import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.model_selection import train_test_split

class SVM:
    # Basic initialization function
    def __init__(self, lr = 0.001, lambda_param = 0.01, gamma = 0.1, n_iter = 1000):
        self.lr = lr
        self.lambda_param = lambda_param
        self.gamma = gamma
        self.n_iter = n_iter
        self.w = None
        self.b = None

    # Function to initialize the weight vector and the bias term with random small values
    def initialize_weights(self, X):
        n_features = X.shape[1]
        self.w = np.random.rand(n_features)
        self.b = 0

    # Function to label the class of each sample as 1 or -1
    def get_label(self, y, label):
        y_ = np.where(y==label, -1, 1)
        return y_
    
    # Fit function to train from data using gradient descent
    def fit(self, X, y, label):
        self.initialize_weights(X)
        labels = self.get_label(y, label)

        for _ in range(self.n_iter):
            for idx, xi in enumerate(X):
                condition = labels[idx]*(np.dot(xi,self.w) + self.b) >=1
                if condition:
                    self.w -= self.lr*(2*self.lambda_param*self.w)
                else:
                    self.w -= self.lr*(2*self.lambda_param*self.w - np.dot(xi,labels[idx]).astype("float"))
                    self.b -= self.lr*labels[idx]

    # Predict function to perform classification over new data points
    def predict(self, X, classifier="linear"):
        if classifier == "linear":
            # predict the label for a new data point assuming a linear function
            pred = np.dot(X, self.w) + self.b
        elif classifier == "rbf":
            pred = np.exp(-self.gamma * np.linalg.norm(X - self.w)**2) + self.b
        else:
            raise ValueError("Please provide a valid classifier!")
        
        return np.sign(pred)
    
    def accuracy(self, y_true, y_pred, label):
        true_labels = self.get_label(y_true, label)
        accuracy = np.sum(true_labels == y_pred) / len(true_labels)
        return accuracy*100

# Load data
df_iris = pd.read_csv(Path(Path().absolute(), "Algorithms for Data Science/HW5/iris.csv"))
X = df_iris.values[:,:4]
y = df_iris.values[:,4]

classes = ["setosa","virginica","versicolor"]
classifiers = ["linear", "rbf"]
print("")
for i in classes:
    print(f"Class: {i}")
    for j in classifiers:
        class_ = i
        classifier = j

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        clf = SVM()
        clf.fit(X_train, y_train, label=class_)
        predictions = clf.predict(X, classifier=classifier)
        print(f"Kernel: {j}, SVM Accuracy: {clf.accuracy(y, predictions,label=class_)}")
    print("")
