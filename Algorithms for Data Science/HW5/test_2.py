import numpy as np
import pandas as pd
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

class SVM:
  def __init__(self, learning_rate=0.01, epochs=100):
    self.learning_rate = learning_rate
    self.epochs = epochs
    self.models = {}

  def fit(self, X, y):
    # One-vs-All approach - separate models for each class
    classes = np.unique(y)
    for class_label in classes:
      # Convert labels to -1/1 for the target class
      y_binary = np.where(y == class_label, 1, -1)
      # Initialize weights and bias
      self.w = np.zeros(X.shape[1])
      self.b = 0

      # Training loop
      for _ in range(self.epochs):
        for i in range(len(X)):
          # Calculate prediction
          prediction = np.dot(self.w, X[i]) + self.b
          # Update weights based on hinge loss
          if prediction * y_binary[i] < 1:
            self.w += self.learning_rate * y_binary[i] * X[i]
            self.b += self.learning_rate * y_binary[i]

      # Store the model for the class
      self.models[class_label] = (self.w, self.b)

  def predict(self, X):
    # Predict for all classes and choose the one with highest score
    predictions = []
    for class_label, (w, b) in self.models.items():
      prediction = np.dot(X, w) + b
      predictions.append(prediction)
    predictions = np.array(predictions).T
    return np.argmax(predictions, axis=0) + 1  # Add 1 to get original class labels

  def score(self, X, y):
    # Predict and calculate accuracy
    y_pred = self.predict(X)
    return accuracy_score(y, y_pred)


# Load Iris data
iris = load_iris()
X = iris.data
y = iris.target

# Train-test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

# Train models with linear and RBF kernels (replace with desired kernel functions)
svm_linear = SVM()
svm_linear.fit(X_train, y_train)
svm_rbf = SVM()  # Replace with your RBF kernel implementation

# Evaluate accuracy for both models
accuracy_linear = svm_linear.score(X_test, y_test)
accuracy_rbf = svm_rbf.score(X_test, y_test)  # Replace with RBF score

print(f"Accuracy (Linear Kernel): {accuracy_linear}")
print(f"Accuracy (RBF Kernel): {accuracy_rbf}")  # Print RBF accuracy

