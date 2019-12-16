import os
import pandas as pd
import numpy as np

from sklearn.pipeline import Pipeline
from sklearn.feature_selection import VarianceThreshold
from sklearn.preprocessing import StandardScaler
from xgboost import XGBClassifier
from sklearn.experimental import enable_iterative_imputer
from sklearn.impute import IterativeImputer
from sklearn.decomposition import PCA
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC, LinearSVC, NuSVC
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import ExtraTreesRegressor, RandomForestClassifier, AdaBoostClassifier, GradientBoostingClassifier
from xgboost import XGBClassifier
from sklearn.metrics import f1_score, classification_report

from sklearn.model_selection import GridSearchCV, RandomizedSearchCV, ParameterGrid
from sklearn import preprocessing, svm, metrics, tree, decomposition
from sklearn.model_selection import cross_validate
from sklearn.linear_model import LogisticRegression
from time import time

source = os.path.expanduser('C:\\Users\\pmeji\\Documents\\FINAL_TESIS\\source\\')
temp = os.path.expanduser('C:\\Users\\pmeji\\Documents\\FINAL_TESIS\\temp\\')
results = os.path.expanduser('C:\\Users\\pmeji\\Documents\\FINAL_TESIS\\results\\')

def metrics_f1(y_test, y_pred):
    f1 = f1_score(y_test, y_pred, average='weighted') 

    if ((y_test.sum()/len(y_test))>0.5):
        y_bench = [1]*len(y_test)
    else:
        y_bench = [0]*len(y_test)

    f2 = f1_score(y_test, y_bench, average='weighted') 
    margen= f1-f2
    return f1, margen


def define_hyper_params():
    clfs = {
        'RF': RandomForestClassifier(n_estimators=100),
        'ET': ExtraTreesClassifier(n_estimators=10, criterion='entropy'),
        'AB': AdaBoostClassifier(DecisionTreeClassifier(max_depth=1), algorithm="SAMME", n_estimators=200),
        'LR': LogisticRegression(penalty='l2', C=1e5, solver='liblinear'),
        'SVM': svm.SVC(kernel='linear', probability=True, random_state=0),
        'GB': GradientBoostingClassifier(learning_rate=0.05, subsample=0.5, max_depth=6, n_estimators=10),
        'NB': GaussianNB(),
        'DT': DecisionTreeClassifier(),
        'SGD': SGDClassifier(loss="hinge", penalty="l2"),
        'KNN': KNeighborsClassifier(n_neighbors=3),
        'XGB': XGBClassifier()
            }

    grid = { 
        'RF':{'Classifier__n_estimators': [1,10,100,1000,10000], 'Classifier__max_depth': [1,5,10,20,50,100], 
              'Classifier__max_features': ['sqrt','log2'],'Classifier__min_samples_split': [2,5,10]},
        'LR': { 'Classifier__penalty': ['l1','l2'], 'Classifier__C': [0.00001,0.0001,0.001,0.01,0.1,1,10]},
        'SGD': { 'Classifier__loss': ['hinge','log','perceptron'], 'Classifier__penalty': ['l2','l1','elasticnet']},
        'ET': { 'Classifier__n_estimators': [1,10,100,1000,10000], 'Classifier__criterion' : ['gini', 'entropy'] ,
               'Classifier__max_depth': [1,5,10,20,50,100], 'Classifier__max_features': ['sqrt','log2'],
               'Classifier__min_samples_split': [2,5,10]},
        'AB': { 'Classifier__algorithm': ['SAMME', 'SAMME.R'], 'Classifier__n_estimators': [1,10,100,1000,10000]},
        'GB': {'Classifier__n_estimators': [1,10,100,1000,10000], 'Classifier__learning_rate' : [0.001,0.01,0.05,0.1,0.5],
               'Classifier__subsample' : [0.1,0.5,1.0], 'Classifier__max_depth': [1,3,5,10,20,50,100]},
        'NB' : {},
        'DT': {'Classifier__criterion': ['gini', 'entropy'], 'Classifier__max_depth': [1,5,10,20,50,100], 
               'Classifier__max_features': ['sqrt','log2'],'Classifier__min_samples_split': [2,5,10]},
        'SVM' :{'Classifier__C' :[0.00001,0.0001,0.001,0.01,0.1,1,10],'Classifier__kernel':['linear', 'rbf']},
        'KNN' :{'Classifier__n_neighbors': [1,5,10,25,50,100],'Classifier__weights': ['uniform','distance'],
                'Classifier__algorithm': ['auto','ball_tree','kd_tree']},
        'XGB':  {'Classifier__learning_rate': [0.2, 0.3, 0.5], 'Classifier__max_depth': [6, 9, 12],
                    'Classifier__subsample': [0.8, 1.0],  'Classifier__colsample_bytree': [0.8, 1.0]} 
           }

    return clfs, grid


def magic_loop(models_to_run, clfs, grid, pipeline, df_train, df_test, estado, search = 1):
    y_train = df_train.semaforo_std.ravel()
    X_train = df_train.drop(['semaforo_std','cct'], axis=1)
    
    y_test = df_test.semaforo_std.ravel()
    X_test = df_test.drop(['semaforo_std','cct'], axis=1)
    
    results_f1 = {}
    margen_f1 = {}
    
    for index, clf in enumerate([clfs[x] for x in models_to_run]):
        model_name = models_to_run[index]
        print(model_name)
        parameter_values = grid[models_to_run[index]]
        parameter_values['PCA__n_components'] = [2,4,6,8,16,32,64]
        try:
            pipeline.set_params(Classifier = clf)
            if(search):
                gs = GridSearchCV(pipeline, parameter_values, cv=5, 
                                  n_jobs=-1, scoring='f1')
            else:
                gs = RandomizedSearchCV(pipeline, parameter_values, cv=5,
                                         n_jobs=-1, scoring='f1')
            start = time()

            gs.fit(X_train, y_train)
            y_pred = gs.predict(X_test)
            
            f1, margen = metrics_f1(y_test, y_pred)

            results_f1[model_name] = f1
            margen_f1[model_name] = margen

            print("GridSearch time: " + (str)(time() - start))

        except IndexError as e:
            print('Error:', e)
            continue

    return results_f1, margen_f1

def results_magic_loop(df_train, df_test, models=['LR','RF','ET','KNN','XGB'], pipeline):
    lista_edos = list(df_train.edo.unique()) + [33]
    
    margen_f1_completo = {}
    results_f1_completo = {}
  
    for estado in lista_edos:
        if estado == 33:
            df_edo_train = df_train
            df_edo_test = df_test
        else:
            df_edo_train = df_train[df_train.edo==estado]
            df_edo_test = df_test[df_test.edo==estado]
    
        if(len(df_edo_train)>0):
            clfs, grid = define_hyper_params()
            results_f1, margen_f1 = magic_loop(models, clfs, grid, pipeline, df_edo_train, df_edo_test, estado, 1)
            margen_f1_completo[estado] = margen_f1
            results_f1_completo[estado] = results_f1
    
    return margen_f1_completo, results_f1_completo

    
def run_selection(num, models, pipeline, nom_pipe):
    nom = "slide_train_" + str(num_window) + ".csv"
    addr= os.path.join(temp, nom)
    df_train1 = pd.read_csv(addr)

    nom = "slide_test_" + str(num_window) + ".csv"
    addr= os.path.join(temp, nom)
    df_test1 = pd.read_csv(addr)

    nom = "slide_train_" + str(num_window) + "_selected.csv"
    addr= os.path.join(temp, nom)
    vars1 = pd.read_csv(addr)

    lista_v = vars1["0"].values.tolist()
    df_train = df_train1[lista_v]
    df_test  = df_test1[lista_v]
    
    margen_S, results_S = results_magic_loop(df_train, df_test,num, models, pipeline)
    nom = "margen_S" + str(num_window) + nom_pipe ".csv"
    addr= os.path.join(results, nom)
    pd.DataFrame(margen_S).transpose().to_csv(addr)
    nom = "results_S" + str(num_window) + nom_pipe ".csv"
    addr= os.path.join(results, nom)
    pd.DataFrame(results_S).transpose().to_csv(addr)
    
    
#==================== Main ============================
    
pipeline = Pipeline([
    ('Iterative Imputer', IterativeImputer(random_state=1996, max_iter = 10, tol=0.01,
                                           estimator=  ExtraTreesRegressor(n_estimators = 300,
                                                                           random_state=0,
                                                                           verbose =True))),
    ('VarianceThreshold', VarianceThreshold()),
    ('Normalizer', StandardScaler()),
    ('Classifier', RandomForestClassifier(n_estimators=1000, n_jobs=-1))
    ])

models = ['LR','RF','ET','KNN','XGB']

run_selection(1, models, pipeline, "_")
run_selection(2, models, pipeline, "_")
run_selection(3, models, pipeline, "_")


pipelinePCA = Pipeline([
    ('Iterative Imputer', IterativeImputer(random_state=1996, max_iter = 10, tol=0.01,
                                           estimator=  ExtraTreesRegressor(n_estimators = 300,
                                                                           random_state=0,
                                                                           verbose =True))),
    ('VarianceThreshold', VarianceThreshold()),
    ('Normalizer', StandardScaler()),
    ('PCA', PCA()),
    ('Classifier', RandomForestClassifier(n_estimators=1000, n_jobs=-1))
    ])

run_selection(1, models, pipelinePCA, "_PCA")
run_selection(2, models, pipelinePCA, "_PCA")
run_selection(3, models, pipelinePCA, "_PCA")