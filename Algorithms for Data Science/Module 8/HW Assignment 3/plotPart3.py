from sklearn.datasets import load_iris
import matplotlib.pyplot as plt
import numpy as np

# Load the Iris dataset
iris = load_iris()

X = iris.data[:, [2, 3]]  # Features (using features 2 and 3)
y = iris.target  # Target labels

h_values = [0.1, 0.25, 0.5]
class_colors = ['r', 'g', 'b']  # Define colors for each class

for h in h_values:
    # Train the Parzen window classifier
    model = ParzenWindowClassifier(h)  # Adjust 'h' (bandwidth) as needed
    model.fit(X, y)
    
    # Generate x-axis values for the features
    x1_values = np.linspace(0.5, 7, 50)  # For feature 2
    x2_values = np.linspace(0, 3, 50)  # For feature 3

    # Create a meshgrid for the points (x1, x2)
    X1, X2 = np.meshgrid(x1_values, x2_values)
    
    # Predict the class labels for each point in the meshgrid
    Z = model.predict(np.c_[X1.ravel(), X2.ravel()])
    
    # Reshape the prediction results to match the shape of the meshgrid
    Z = np.array(Z).reshape(X1.shape)
    
    # Plot the decision boundary and points colored by class
    plt.contourf(X2, X1, Z, alpha=0.3, cmap='viridis', levels=np.arange(len(model.classes) + 1) - 0.5)  # Decision boundary
    for class_index in range(len(model.classes)):
        class_data = model.class_distributions[class_index]
        plt.scatter(class_data[:, 1], class_data[:, 0], marker='o', label=f"Class {model.classes[class_index]} Points", color=class_colors[class_index])

    plt.xlabel("Feature petal width")
    plt.ylabel("Feature petal length")
    plt.title(f"Decision Boundary and Data Points - Features petal width and petal length (h={h})")
    plt.legend()
    plt.show()