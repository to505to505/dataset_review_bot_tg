import pandas as pd
import matplotlib.pyplot as plt 
import seaborn as sns
import numpy as np
import scipy.stats as stats
import df2img
import ast
from utilities import *


DATA_URL = '/Users/dmitrysakharov/Documents' 
img_url = f"{DATA_URL}/dataset_review/data/img"
prepdata_url = f"{DATA_URL}/dataset_review/data/prep_data"
input_url = f"{DATA_URL}/dataset_review/data/inputs"
button_text = 122121218821827178

pd.set_option('display.float_format', lambda x: '%.3f' % x)

def read_data(ID):
    data = pd.read_csv(f"{input_url}/D{ID}.csv", index_col=False)
    return data

def get_data_variables(data, ID):
    data = data.copy()
    n_nan = data.isna().sum().sum()

    for col in data.columns:
        data[col] = data[col].fillna(data[col].mode()[0])

    n_samples, n_features = data.shape
    cat_features = []
    num_features = []
    bin_features = []

    for col in data.columns:
        if data[col].dtypes == "O" or data[col].nunique()==2:
            cat_features.append(col)
            if data[col].nunique()==2:
                bin_features.append(col)
        else:
            num_features.append(col)

    n_bin_features = len(bin_features)
    n_cat_features = len(cat_features)
    n_num_features = len(num_features)

    var_dict = {"n_samples":n_samples, "n_features":n_features,
    "cat_features":cat_features, "n_cat_features":n_cat_features,
    "num_features":num_features, "n_num_features":n_num_features,
    "bin_features":bin_features, "n_bin_features":n_bin_features, "n_nan":n_nan}

    with open(f"{prepdata_url}/data_vars{ID}.txt", "w") as file:
        file.write(str(var_dict))

    return var_dict

def auto_preproccecing(data, data_vars, ID):
    data = data.copy()
    isna_df = data.isna().sum()/len(data)
    na_features_to_drop = isna_df[isna_df >= 0.7].index.values
    
    #imputation
    for feature in data_vars["cat_features"]:
        data[feature] = data[feature].fillna(data[feature].mode()[0])
    for feature in data_vars["num_features"]:
        data[feature] = data[feature].fillna(data[feature].median())
        
    nunique_df = pd.DataFrame()
    for feature in data.drop(na_features_to_drop, axis=1).select_dtypes("O").columns.values:
        nunique_df.loc[feature, "n_unique"] = data[feature].nunique()/len(data)
    
    many_unique_values_features_to_drop = nunique_df.loc[nunique_df["n_unique"] > 0.03, "n_unique"].index.values
    
    data = data.drop(na_features_to_drop, axis = 1)
    data = data.drop(many_unique_values_features_to_drop, axis = 1)
    
    skew_df = pd.DataFrame({"features":data.select_dtypes(np.number).columns.values}).set_index("features")
    skew_df["skew"] = stats.skew(data.select_dtypes(np.number))
    for feature in skew_df.loc[np.abs(skew_df["skew"]) > 1.5].index.values:
        if data[feature].min() >= 0:
            data[feature] = np.log1p(data[feature])
            #data = data.drop([feature], axis=1)
    skew_df["skew_new"] = stats.skew(data.select_dtypes(np.number))
    rows_before = data.shape[0]
    rows_after = data.shape[0]

    skew_df.to_csv(f"{prepdata_url}/skew_df{ID}.csv")
    data.to_csv(f"{prepdata_url}/D{ID}.csv")

    return data, na_features_to_drop, many_unique_values_features_to_drop, rows_before, rows_after, data_vars["cat_features"], data_vars["num_features"], data_vars["bin_features"]

    
def get_ttest(data, ID, bf):
    data = data.copy()
    f1 = data[bf].unique()[0]
    f2 = data[bf].unique()[1]
    df1 = data[data[bf]==f1]
    df2 = data[data[bf]==f2]
    
    with open(f"{prepdata_url}/data_vars{ID}.txt", "r") as file:
        data_vars = ast.literal_eval(file.read())
    num_features = data_vars["num_features"]
    
    twov_df = pd.DataFrame({"Features":num_features}).set_index("Features")
    
    for col in num_features:
        value, p_val = stats.ttest_ind(df1[col], df2[col])
        value, p_val = np.round(value, 4), np.round(p_val, 4)
        twov_df.loc[col, "Two-Sided p-value "] = "test_value: " + str(value) + ", " + "p_val: " + str(p_val)
        
        value, p_val = stats.ttest_ind(df1[col], df2[col], alternative="greater")
        value, p_val = np.round(value, 4), np.round(p_val, 4)
        twov_df.loc[col, f"'{f1}' greater '{f2}' "] = "test_value: " + str(value) + ", " + "p_val: " + str(p_val)
        
        value, p_val = stats.ttest_ind(df1[col], df2[col], alternative="less")
        value, p_val = np.round(value, 4), np.round(p_val, 4)
        twov_df.loc[col, f"'{f1}' less '{f2}' "] = "test_value: " + str(value) + ", " + "p_val: " + str(p_val)
    
    twov_df = twov_df.round(4)
    
    twov_df.to_csv(f"{prepdata_url}/twov{ID}.csv")
    
def get_manna(data, ID, bf):
    data = data.copy()
    f1 = data[bf].unique()[0]
    f2 = data[bf].unique()[1]
    df1 = data[data[bf]==f1]
    df2 = data[data[bf]==f2]
    
    with open(f"{prepdata_url}/data_vars{ID}.txt", "r") as file:
        data_vars = ast.literal_eval(file.read())
    num_features = data_vars["num_features"]
    
    twov_df = pd.DataFrame({"Features":num_features}).set_index("Features")
    
    for col in num_features:
        value, p_val = stats.mannwhitneyu(df1[col], df2[col])
        value, p_val = np.round(value, 4), np.round(p_val, 4)
        twov_df.loc[col, "Two-Sided p-value"] = "test_value: " + str(value) + "-" + "p_val: " + str(p_val)
        
        value, p_val = stats.mannwhitneyu(df1[col], df2[col], alternative="greater")
        value, p_val = np.round(value, 4), np.round(p_val, 4)
        twov_df.loc[col, f"'{f1}' greater '{f2}' p-value"] = "test_value: " + str(value) + "-" + "p_val: " + str(p_val)
        
        value, p_val = stats.mannwhitneyu(df1[col], df2[col], alternative="less")
        value, p_val = np.round(value, 4), np.round(p_val, 4)
        twov_df.loc[col, f"'{f1}' less '{f2}' p-value"] = "test_value: " + str(value) + "-" + "p_val: " + str(p_val)
    
    twov_df = twov_df.round(4)
    
    
    twov_df.to_csv(f"{prepdata_url}/twov{ID}.csv")

def get_corr_pearson(data, data_vars, ID):
    data = data.copy()
    
    with open(f"{prepdata_url}/data_vars{ID}.txt", "r") as file:
            data_vars = ast.literal_eval(file.read())
    
    corr = data[data_vars["num_features"]].corr()
    corr = corr.round(4)
    
    cols = data[data_vars["num_features"]].columns.array
    pval_df = pd.DataFrame()
    for col1 in cols:
        for col2 in cols:
            _, p_val = stats.pearsonr(data[col1], data[col2])
            pval_df.loc[col1, col2] = p_val
    pval_df = pval_df.round(4)
    
    plt.clf()
    plt.figure(figsize=(11.5,11.5))
    fig_corr = sns.heatmap(corr, annot=True, center=True)
    fig = fig_corr.get_figure()
    
    fig.savefig(f"{img_url}/snscorr{ID}.png")
    corr.to_csv(f"{prepdata_url}/corr{ID}.csv")
    pval_df.to_csv(f"{prepdata_url}/p_val{ID}.csv")

def get_corr_spearman(data, data_vars, ID):
    data = data.copy()
    
    with open(f"{prepdata_url}/data_vars{ID}.txt", "r") as file:
            data_vars = ast.literal_eval(file.read())
    
    corr = data[data_vars["num_features"]].corr(method = "spearman")
    corr = corr.round(4)
    
    cols = data[data_vars["num_features"]].columns.array
    pval_df = pd.DataFrame()
    for col1 in cols:
        for col2 in cols:
            _, p_val = stats.spearmanr(data[col1], data[col2])
            pval_df.loc[col1, col2] = p_val
    pval_df = pval_df.round(4)
    
    plt.clf()
    plt.figure(figsize=(11.5,11.5))
    fig_corr = sns.heatmap(corr, annot=True, center=True)
    fig = fig_corr.get_figure()
    
    fig.savefig(f"{img_url}/snscorr{ID}.png")
    corr.to_csv(f"{prepdata_url}/corr{ID}.csv")
    pval_df.to_csv(f"{prepdata_url}/p_val{ID}.csv")
    

def descriptive(data, ID): 
    with open(f"{prepdata_url}/data_vars{ID}.txt", "r") as file:
        data_vars = ast.literal_eval(file.read())
    numeric1 = data_vars["num_features"]
    data = data.copy()
    data_d = data[numeric1].describe().round(3)
    v=1
    coef = 1
    for i in range(0, data_d.shape[1], 9):
        plt.clf()
        if data_d.iloc[:, i:i+9].shape[1]==1: 
            coef = 2.4
        elif data_d.iloc[:, i:i+9].shape[1]==2:
            coef = 1.85
        elif data_d.iloc[:, i:i+9].shape[1]==3:
            coef =1.45
        elif data_d.iloc[:, i:i+9].shape[1]==4:
            coef =1.25
        elif data_d.iloc[:, i:i+9].shape[1]==5:
            coef = 1.15
        elif data_d.iloc[:, i:i+9].shape[1]==6:
            coef = 1.1   
        
        else: 
            pass
        fig_descriptive = df2img.plot_dataframe(
        data_d.iloc[:, i:i+9],
        title=dict(
                font_color="black",
                font_family="Times New Roman",
                font_size=16,
                text=f"Descriptive statistics of numeric featuers {str(v*(data_d.shape[1]>9)).replace('0', ' ')}",
            ),
            tbl_header=dict(
                align="right",
                fill_color="pink",
                font_color="black",
                font_size=8.5,
                line_color="black",
            ),
            tbl_cells=dict(
                align="right",
                line_color="black",
            ),
            row_fill_color=("#ffffff", "#ffffff"),
            fig_size=(data_d.iloc[:, i:i+9].shape[1]*165*coef, 300),
        )
        fig_descriptive.write_image(file=f"{img_url}/descriptive{v}_{ID}.png", format='png')
        v+=1

def graphs(data, ID):
    with open(f"{prepdata_url}/data_vars{ID}.txt", "r") as file:
        data_vars = ast.literal_eval(file.read())
    num_features = data_vars["num_features"]
    cat_features = data_vars["cat_features"]
    n_cat_features = data_vars["n_cat_features"]
    n_num_features = data_vars["n_num_features"]
    text_r = ''

    for v, feat in enumerate(num_features):
        plt.clf()
        plt.figure(facecolor='white')
        fig_graph = sns.histplot(data=data, x=feat, bins=40, stat='density', common_norm=False, color='pink')
        fig_graph.get_figure()
        plt.title(f"Density Histogram of {feat}")
        plt.savefig(f"{img_url}/graphs_n_{v}_{ID}.png")
    
    for v, feat in enumerate(cat_features):
        try:
            plt.clf()
            plt.figure(facecolor='white')
            fig_graph = sns.countplot(data=data, x=feat, color='pink')
            fig_graph.get_figure()
            plt.title(f"Countplot of {feat}")
            plt.savefig(f"{img_url}/graphs_c_{v}_{ID}.png")
        except ValueError:
            text_r = text_r + f"Oops!  I could not draw the countplot of {feat}, maybe there are too much unique values.\n"
    return text_r


    