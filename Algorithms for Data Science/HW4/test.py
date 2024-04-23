import numpy as np
import pandas as pd
from sklearn.datasets import load_iris
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split


class RBFNN_2:

    def __init__(self) -> None:
        self.model_error = 0
        self.w_hat = []
        self.w = []
        self.spread = 0
        self.predictions = []

    def fit(self, X, y, spread=None):
        if spread is None:
            spread = 0.5
        
        n, d = X.shape
        H = np.zeros((n,n))

        for j in range(0,n):
            for i in range(0,n):
                W = X[j,:]
                H[i,j] = np.exp(-(np.linalg.norm(X[i,:]-W))**2 / (2*spread**2))
        W_hat = np.dot(np.dot(np.linalg.pinv(np.dot(H.conj().T, H)),H.conj().T),y)
        # W_hat = np.linalg.pinv(H) * y
        yt = np.dot(H, W_hat)
        y_pred = np.ones((y.shape[0],1))
        y_pred[yt < 0] = -1
        pred_error = 1 - np.sum(y == y_pred)/y.shape[0]

        self.w_hat = W_hat
        self.w = X
        self.spread = spread
        self.model_error = pred_error

    def classify(self, X):

        n1, d1 = X.shape
        n2, d2 = self.w.shape

        H = np.zeros((n1,n2))
        for j in range(0,n2):
            for i in range(0,n1):
                W = self.w[j,:]
                H[i,j] = np.exp(-(np.linalg.norm(X[i,:]-W))**2 / (2*self.spread**2))

        y = np.dot(H, self.w_hat)
        y_hat = np.zeros((n1,1))
        for i in range(0,n1):
            for j in range(0,n2):
                W = self.w[j,:]
                W_hat = self.w_hat[j]
                y_hat[i] = y_hat[i] + W_hat*np.exp(-(np.linalg.norm(X[i,:]-W))**2 / (2*self.spread**2))
        y_pred = np.ones(y.shape)
        y_pred[y < 0] = -1
        self.predictions = y_pred
        return y_pred
    
    def accuracy_score(self, X, y):
        return (1 - np.sqrt(np.sum((self.predictions - y)**2))/y.shape[0])*100


# iris = pd.read_csv("/Users/zachhatzenbeller/Documents/GitHub/Data-Science-Masters/Algorithms for Data Science/HW4/iris.csv")
iris = pd.read_csv(r"C:\Users\zhatz\Documents\GitHub\Data-Science-Masters\Algorithms for Data Science\HW4\iris.csv")

X = iris.iloc[:,:4].values
y = iris.iloc[:,4].values
y1 = y.copy()
y2 = y.copy()
y3 = y.copy()

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)

y1[(y1 == "versicolor") | (y1 == "virginica")] = -1
y1[y1 == "setosa"] = 1

y2[(y2 == "setosa") | (y2 == "virginica")] = -1
y2[y2 == "versicolor"] = 1

y3[(y3 == "versicolor") | (y3 == "setosa")] = -1
y3[y3 == "virginica"] = 1

y1 = y1.reshape(-1,1)
y2 = y2.reshape(-1,1)
y3 = y3.reshape(-1,1)

X_test = np.array([
    [5.1,3.5,1.4,0.2],
    [4.9,3.0,1.4,0.2],
    [4.7,3.2,1.3,0.2],
    [4.6,3.1,1.5,0.2],
    [5.0,3.6,1.4,0.2],
    [7.0,3.2,4.7,1.4],
    [6.4,3.2,4.5,1.5],
    [6.9,3.1,4.9,1.5],
    [5.5,2.3,4.0,1.3],
    [6.5,2.8,4.6,1.5],
])

y_test = np.array([
    [-1],
    [-1],
    [-1],
    [-1],
    [-1],
    [1],
    [1],
    [1],
    [1],
    [1]
])

neural_network = RBFNN_2()
neural_network.fit(X[:25],y1[:25])
# neural_network.classify(X_test)
print(neural_network.model_error)
array = neural_network.classify(X)
accuracy = neural_network.accuracy_score(X, y1)
print(accuracy)
print(array[array > 0].shape)
