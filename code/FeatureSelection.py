import os
import pandas as pd
import numpy as np

from sklearn.impute import SimpleImputer, IterativeImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from xgboost import XGBClassifier
from sklearn.ensemble import ExtraTreesRegressor, RandomForestClassifier
from sklearn.feature_selection import RFECV
from sklearn.model_selection import StratifiedKFold
from sklearn.feature_selection import VarianceThreshold

source = os.path.expanduser('C:\\Users\\pmeji\\Documents\\FINAL_TESIS\\source\\')
temp = os.path.expanduser('C:\\Users\\pmeji\\Documents\\FINAL_TESIS\\temp\\')


def remove_missing(df):
    #Deals with infinity values
    df[df==np.inf]=np.nan
    df[df==-np.inf]=np.nan

    print(len(df), len(df.columns))
    #Deal with missing values. Drop columns missing more than 20% missing values
    df.dropna(axis=1, thresh = 4*len(df)/5, inplace=True)
    #Deal with missing values. Drop rows missing more than 20% missing values
    df.dropna(axis=0, thresh = 4*len(df.columns)/5, inplace=True)
    print(len(df), len(df.columns))   
    return df

def remove_correlated(df, tresh=0.95):
    # Create correlation matrix
    corr_matrix = df.corr().abs()

    # Select upper triangle of correlation matrix
    upper = corr_matrix.where(np.triu(np.ones(corr_matrix.shape), k=1).astype(np.bool))

    # Find index of feature columns with correlation greater than 0.95
    to_drop = [column for column in upper.columns if any(upper[column] > 0.95)]
    print(to_drop)
    print(len(to_drop))

    # Drop features 
    df_new = df.drop(df[to_drop], axis=1)
    return df_new

#https://ramhiser.com/post/2018-03-25-feature-selection-with-scikit-learn-pipeline/
class PipelineRFE(Pipeline):

    def fit(self, X, y=None, **fit_params):
        super(PipelineRFE, self).fit(X, y, **fit_params)
        self.feature_importances_ = self.steps[-1][-1].feature_importances_
        return self
    

def variable_selection(feature_selector_cv, df):
    estados = list(range(1,34))
    lista_vars = []
    for edo in estados:
        if edo == 33:
            df_edo = df
        else:
            df_edo = df[df.edo ==edo]
        if len(df_edo)>0:
            y = df.semaforo_std.ravel()
            X = df.drop(['cct', 'semaforo_std'], axis=1)
            
            feature_selector_cv.fit(X, y)
            feature_selector_cv.n_features_
            cv_grid_f1 = np.sqrt(-feature_selector_cv.grid_scores_)
            feature_names = X.columns
            selected_features = feature_names[feature_selector_cv.support_].tolist()

            union = list(set(lista_vars) | set(selected_features))
            lista_vars = union

    df_select = df[lista_vars]
    df_select = remove_correlated(df_select)
    return list(df_select.columns) + ['cct', 'semaforo_std']
    
def run_selection(filename, feature_selector_cv):
    addr= os.path.join(source, filename)
    df_train = pd.read_csv(addr)
    df = remove_missing(df_train)

    selected_vars  = pd.DataFrame(variable_selection(feature_selector_cv, df))
    new_filename = filename[:4] + "_selected.csv"
    addr= os.path.join(temp, new_filename)
    selected_vars.to_csv(addr, index = False)
    
#==================== Main ============================

#First stage
pipeline = PipelineRFE([
    ('SimpleImputer',  SimpleImputer(missing_values=np.nan, strategy='median')),
    ('VarianceThreshold', VarianceThreshold()),
    ('Normalizer', StandardScaler()),
    ('Classifier', RandomForestClassifier(n_estimators=600, n_jobs=-1))
])
_ = StratifiedKFold(random_state=1996)
feature_selector_cv = RFECV(pipeline, cv=8, step=10, 
                        scoring="f1")

run_selection("slide_train_1_raw.csv", feature_selector_cv)
run_selection("slide_train_2_raw.csv", feature_selector_cv)
run_selection("slide_train_3_raw.csv", feature_selector_cv)

#Second stage
pipeline = PipelineRFE([
    ('Iterative Imputer', IterativeImputer(random_state=1996, max_iter = 10, tol=0.01,
                                           estimator=  ExtraTreesRegressor(n_estimators = 300,
                                                                           random_state=0,
                                                                           verbose =True))),
    ('VarianceThreshold', VarianceThreshold()),
    ('Normalizer', StandardScaler()),
    ('Classifier', RandomForestClassifier(n_estimators=600, n_jobs=-1))
])
_ = StratifiedKFold(random_state=1996)
feature_selector_cv = RFECV(pipeline, cv=8, step=10, 
                        scoring="f1")

run_selection("slide_train_1.csv", feature_selector_cv)
run_selection("slide_train_2.csv", feature_selector_cv,)
run_selection("slide_train_3.csv", feature_selector_cv)
