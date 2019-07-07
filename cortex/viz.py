"""
Copyright 2019 Cognitive Scale, Inc. All Rights Reserved.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

  http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import matplotlib.pyplot as plt
import seaborn as sns


class Viz:

    """
    A wrapper that assists users in running multiple commonly used visualizations on the same dataframe; not meant to be directly instantiated by clients.
    """

    def __init__(self, df, figsize=(18, 9)):
        self.df = df
        self.corr_m = df.corr()

        if figsize is None or not isinstance(figsize, tuple):
            self.figsize = (18, 9)
        else:
            self.figsize = figsize

    def show_corr(self, column: str):
        cm_sorted = self.corr_m[column].sort_values(ascending=False)
        plt.rcParams['figure.figsize'] = self.figsize
        plt.xticks(rotation=90)
        sns.barplot(x=cm_sorted.index, y=cm_sorted)
        plt.show()
        plt.clf()

    def show_corr_heatmap(self, **kwargs):
        plt.rcParams['figure.figsize'] = self.figsize
        sns.heatmap(self.corr_m, annot=True, cmap=kwargs.get('cmap', 'BuGn'), robust=True, fmt=kwargs.get('fmt', '.1f'))
        plt.show()
        plt.clf()

    def show_dist(self, column: str):
        try:
            from scipy.stats import norm
            fit = norm
        except ImportError:
            fit = None

        plt.rcParams['figure.figsize'] = self.figsize
        sns.distplot(self.df[column], fit=fit)
        plt.show()
        plt.clf()

    def show_probplot(self, column: str):
        try:
            from scipy import stats
            plt.rcParams['figure.figsize'] = self.figsize
            stats.probplot(self.df[column], plot=plt)
            plt.show()
            plt.clf()
        except ImportError:
            raise Exception('show_probplot requires SciPy to be installed')

    def show_corr_pairs(self, column: str, threshold=0.7):
        cm = self.df.corr()
        values = list(cm[column].values)
        keys = list(cm[column].keys())
        vars = [i for i in keys if values[keys.index(i)] > threshold]

        plt.rcParams['figure.figsize'] = self.figsize
        sns.pairplot(self.df, height=3, vars=vars)
        plt.show()
        plt.clf()