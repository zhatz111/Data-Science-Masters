import pandas as pd
import numpy as np
from pathlib import Path
import matplotlib.pyplot as plt
from numpy.linalg import eigh
import math
from scipy.stats.distributions import chi2
from scipy import stats

# %matplotlib inline


class sigma_ellipse_plot:

    def __init__(
        self,
        df=None,
        target="setosa",
        target_header="species",
        feature1="sepal_length",
        feature2="petal_width",
        std_devs=[1, 2, 3],
    ):

        self.data = df
        self.target = target
        self.feature1 = feature1
        self.feature2 = feature2
        self.target_header = target_header
        self.std_devs = std_devs
        self.largest_eigenvalue = None
        self.largest_eigenvector = None
        self.smallest_eigenvalue = None
        self.smallest_eigenvector = None
        self.angle = None
        self.mean = None
        self.r_ellipses = None
        self.mu_X = None
        self.mu_Y = None
        self.chisquare_val = None

    def get_data(self):

        self.data = self.data[self.data[self.target_header] == self.target].drop(
            self.target_header, axis=1
        )[[self.feature1, self.feature2]]

        return

    def get_eigens(self):

        covariance_matrix = self.data.cov()
        eigenvalues, eigenvectors = eigh(covariance_matrix)

        self.largest_eigenvector = eigenvectors[np.argmax(eigenvalues)]
        self.largest_eigenvalue = np.max(eigenvalues)
        self.smallest_eigenvector = eigenvectors[np.argmin(eigenvalues)]
        self.smallest_eigenvalue = np.min(eigenvalues)

        return

    def get_angle(self):

        self.angle = math.atan2(
            self.largest_eigenvector[1], self.largest_eigenvector[0]
        )

        return

    def shift_angle(self):

        if self.angle < 0:
            self.angle = self.angle + 2 * math.pi

        return

    def get_mean(self):

        self.mean = self.data.mean()

        return

    def get_chisquare_vals(self):

        self.chisquare_val = []
        for i in range(0, len(self.std_devs)):
            percent_covered = stats.norm.cdf(self.std_devs[i]) - stats.norm.cdf(
                self.std_devs[i] * -1
            )
            self.chisquare_val.append((chi2.ppf(percent_covered, df=2)) ** 0.5)

        return self.chisquare_val

    def get_ellipses(self):

        chisquare_val = self.get_chisquare_vals()

        self.r_ellipses = []
        for i in range(0, len(self.std_devs)):
            theta_grid = np.linspace(0, 2 * math.pi, 100)
            phi = self.angle
            self.mu_X = self.mean[0]
            self.mu_Y = self.mean[1]
            a = chisquare_val[i] * math.sqrt(self.largest_eigenvalue)
            b = chisquare_val[i] * math.sqrt(self.smallest_eigenvalue)

            ellipse_x_r = a * np.cos(theta_grid)
            ellipse_y_r = b * np.sin(theta_grid)

            R = [[math.cos(phi), math.sin(phi)], [-math.sin(phi), math.cos(phi)]]

            ellipses = np.array([ellipse_x_r, ellipse_y_r])

            r_ellipse = ellipses.T.dot(R).T

            self.r_ellipses.append(r_ellipse)

        return

    def get_labels(self, special_phrase=None):

        labels = []
        for i in range(0, len(self.std_devs)):

            if special_phrase is None:
                label = str(self.std_devs[i]) + " std. dev. from mean"
                labels.append(label)
            else:
                label = special_phrase + str(self.std_devs[i]) + " std. dev. from mean"
                labels.append(label)

        return labels

    def pipeline(self):

        self.get_data()
        self.get_eigens()
        self.get_angle()
        self.shift_angle()
        self.get_mean()
        self.get_ellipses()

        return self.data, self.r_ellipses, self.mu_X, self.mu_Y


if __name__ == "__main__":

    df = pd.read_csv(
        Path(Path().absolute(), "Algorithms for Data Science/HW5/iris.csv")
    )
    feature1 = "sepal_length"
    feature2 = "petal_width"

    for target in df["species"].unique():
        setosa_ellipses_obj = sigma_ellipse_plot(
            df=df, target=target, feature1=feature1, feature2=feature2
        )
        setosa_df, setosa_ellipses, setosa_mu_X, setosa_mu_Y = (
            setosa_ellipses_obj.pipeline()
        )
        setosa_plot_labels = setosa_ellipses_obj.get_labels()

        plt.figure(figsize=(20, 10))

        colors_for_plot = ["g", "b", "r"]
        for i in range(0, len(setosa_ellipses)):
            plt.plot(
                setosa_ellipses[i][0] + setosa_mu_X,
                setosa_ellipses[i][1] + setosa_mu_Y,
                colors_for_plot[i],
                label=setosa_plot_labels[i],
            )

        plt.scatter(
            setosa_df[feature1],
            setosa_df[feature2],
            c="blue",
            s=3,
            label=f"{target} raw data",
        )

        if target == "setosa":
            outlier_index = 43
            ###############
            plt.plot(
                setosa_df[feature1][outlier_index],
                setosa_df[feature2][outlier_index],
                marker="o",
                color="r",
                markersize=12,
                fillstyle="none",
                label="setosa_outlier",
            )
            ###############

        plt.scatter(setosa_mu_X, setosa_mu_Y, c="blue", s=40, label=f"{target} mean")


        # df_removal = df.copy().drop(index=43)
        # setosa_ellipses_obj = sigma_ellipse_plot(
        #     df=df_removal, target=target, feature1=feature1, feature2=feature2
        # )
        # setosa_df, setosa_ellipses, setosa_mu_X, setosa_mu_Y = (
        #     setosa_ellipses_obj.pipeline()
        # )
        # setosa_plot_labels = setosa_ellipses_obj.get_labels()

        # colors_for_plot = ["c", "m", "y"]
        # for i in range(0, len(setosa_ellipses)):
        #     plt.plot(
        #         setosa_ellipses[i][0] + setosa_mu_X,
        #         setosa_ellipses[i][1] + setosa_mu_Y,
        #         colors_for_plot[i],
        #         label=f" New {setosa_plot_labels[i]}",
        #     )

        plt.xlabel("Sepal Length", fontsize=10)
        plt.ylabel("Petal Width", fontsize=10)
        plt.title(f"{target} Class")
        plt.legend()

        plt.show()
