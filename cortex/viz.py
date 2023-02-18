"""
Copyright 2021 Cognitive Scale, Inc. All Rights Reserved.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

  https://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import matplotlib.pyplot as plt
import seaborn as sns

from .exceptions import VisualisationException


class Viz:

    """
    A wrapper that assists users in running multiple commonly used visualizations
    on the same dataframe; not meant to be directly instantiated by clients.
    """

    def __init__(self, df, figsize=(18, 9)):  # pylint: disable=invalid-name
        self.data_frame = df
        self.corr_m = df.corr()

        if figsize is None or not isinstance(figsize, tuple):
            self.figsize = (18, 9)
        else:
            self.figsize = figsize

    def show_corr(self, column: str):
        """_summary_

        Args:
            column (str): _description_
        """
        cm_sorted = self.corr_m[column].sort_values(ascending=False)
        plt.rcParams["figure.figsize"] = self.figsize
        plt.xticks(rotation=90)
        sns.barplot(x=cm_sorted.index, y=cm_sorted)
        plt.show()
        plt.clf()

    def show_corr_heatmap(self, **kwargs):
        """_summary_"""
        plt.rcParams["figure.figsize"] = self.figsize
        sns.heatmap(
            self.corr_m,
            annot=True,
            cmap=kwargs.get("cmap", "BuGn"),
            robust=True,
            fmt=kwargs.get("fmt", ".1f"),
        )
        plt.show()
        plt.clf()

    def show_dist(self, column: str):
        """_summary_

        Args:
            column (str): _description_
        """
        try:
            from scipy.stats import norm  # pylint: disable=import-outside-toplevel

            fit = norm
        except ImportError:
            fit = None

        plt.rcParams["figure.figsize"] = self.figsize
        sns.distplot(self.data_frame[column], fit=fit)
        plt.show()
        plt.clf()

    def show_probplot(self, column: str):
        """_summary_

        Args:
            column (str): _description_

        Raises:
            Exception: _description_
        """
        try:
            from scipy import stats  # pylint: disable=import-outside-toplevel

            plt.rcParams["figure.figsize"] = self.figsize
            stats.probplot(self.data_frame[column], plot=plt)
            plt.show()
            plt.clf()
        except ImportError as exc:
            raise VisualisationException(
                "show_probplot requires SciPy to be installed"
            ) from exc

    def show_corr_pairs(self, column: str, threshold=0.7):
        """_summary_

        Args:
            column (str): _description_
            threshold (float, optional): _description_. Defaults to 0.7.
        """
        corr_map = self.data_frame.corr()
        values = list(corr_map[column].values)
        keys = list(corr_map[column].keys())
        variables = [i for i in keys if values[keys.index(i)] > threshold]

        plt.rcParams["figure.figsize"] = self.figsize
        sns.pairplot(self.data_frame, height=3, vars=variables)
        plt.show()
        plt.clf()
