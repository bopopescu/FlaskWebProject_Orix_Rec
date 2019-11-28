print(__doc__)


# Code source: Gaël Varoquaux
#              Andreas Müller
# Modified for documentation by Jaques Grobler
# License: BSD 3 clause

import numpy as np

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.datasets import make_moons, make_circles, make_classification
from sklearn.neural_network import MLPClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.gaussian_process import GaussianProcessClassifier
from sklearn.gaussian_process.kernels import RBF
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, AdaBoostClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.discriminant_analysis import QuadraticDiscriminantAnalysis
from sklearn.metrics import f1_score
from sklearn.metrics import recall_score
from sklearn.metrics import confusion_matrix
from sklearn.decomposition import PCA #主成分分析器

import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from matplotlib.backends.backend_pdf import PdfPages
plt.rcParams["font.family"] = "Times New Roman"      #全体のフォントを設定
#plt.rcParams["font.size"] = 12

import os
import pandas as pd

from scipy.cluster.hierarchy import linkage, dendrogram
import seaborn as sns

from module import cluster_utils

import datetime
from module.database.Mysql3 import Mysql3



#risk_best_list = mysql.sql_excute_fetch(sql)

dataset_folder = "dataset"
dataset_name = "data_analy_GT_notNAN4.csv"
dataset_path = dataset_folder + "/" + dataset_name
#df = pd.read_csv("wine.txt", sep="\t", index_col=0)
df = pd.read_csv(dataset_path, sep=',')

rank_dict = {}
col_list = df_rank.columns
for var in col_list:
    df_rank = df.rank(numeric_only=True, method='min')
    df_sort = df.sort_values(var).reset_index()
    df_sort2 = df_sort.query('drive_recorder_id == 12325')
    df_index = df_sort2.index[0]
    rank_dict['{}_rank'.format(var)] = df_index







