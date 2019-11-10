import os
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn import metrics
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import accuracy_score
from sklearn.metrics import f1_score
from sklearn.ensemble import ExtraTreesRegressor as ETRg
from math import sqrt, floor
from sklearn.model_selection import GridSearchCV


class CleanData():
    
    def fill_missings(self, df):
        print(df.isnull().sum().sum())
        features = df.columns[df.isnull().sum()==0].tolist()
        if 'cct' in features:
            features.remove('cct')
        if 'Unnamed' in features:
            features.remove('Unnamed')
        if 'semaforo_std' in features:
            features.remove('semaforo_std')

        missingVars = df.columns[df.isnull().sum()>0].tolist()

        for obj in missingVars:
            Etr = ETRg()
            X_train = df[features][df[obj].notnull()] 
            y_train = df[obj][df[obj].notnull()]
            X_test = df[features][df[obj].isnull()] 
            Etr.fit(X_train,np.ravel(y_train)) 
            Pred = Etr.predict(X_test)
            df.loc[df[obj].isnull(), obj] = Pred
            print(df.isnull().sum().sum())

        print(df.isnull().sum().sum())
        return df


    def clean_data(self, df):
        #Remove string and objetive variable
        X = df.drop(['cct'], axis=1)
        X = X.drop(['semaforo_std'], axis=1)
        X_cct = df[['cct', 'semaforo_std','diferencia']]

        X = X.apply(pd.to_numeric)
        X_num = X.select_dtypes(include = ['float', 'int']) #Exclude string variables.

        #Deals with infinity values
        X_num[X_num==np.inf]=np.nan
        X_num[X_num==-np.inf]=np.nan

        #Deal with missing values. Drop columns missing more than 20% missing values
        X_num.dropna(axis=1, thresh = 4*len(X_num)/5, inplace=True)
        #Deal with missing values. Drop rows missing more than 20% missing values
        X_num.dropna(axis=0, thresh = 4*len(X_num.columns)/5, inplace=True)
        #Impute values for the columns with less than 20% missing values
        X_num = self.fill_missings(X_num)
        
        #Escala los resultados
        X_num =  preprocessing.StandardScaler(X_num)

        indices_to_keep = ~X_num.isin([np.nan, np.inf, -np.inf]).any(1)
        X_num = X_num[indices_to_keep]
        X_cct = X_cct[indices_to_keep]

        df_new = X_cct.join(X_num)
        df_new.reset_index(drop=True, inplace=True)

        #nan_val should always be cero
        nan_val = df_new.columns[df_new.isna().any()].tolist()
        for vari in nan_val:
            df_new[vari] = df_new[vari].fillna(0)

        return df_new 


    def remove_correlated(self, df):
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

    def compact_data(self, df):
        #Compress data
        df[df.select_dtypes(include = ['float64']).columns] \
         = df.select_dtypes(include = ['float64']).astype(np.float16)
        df[df.select_dtypes(include = ['int64']).columns] \
        = df.select_dtypes(include = ['int64']).astype(np.int16)
        df[df.select_dtypes(include = ['float32']).columns] \
        = df.select_dtypes(include = ['float32']).astype(np.float16)
        df[df.select_dtypes(include = ['int32']).columns] \
        = df.select_dtypes(include = ['int32']).astype(np.int16)
        return df
    
    #Feature extraction: Exclude
    def exclude(X, var_tresh):
        X_num = X.select_dtypes(include = ['float', 'int']) 
        #Removes variables with low variance
        #Normalizes variables
        X_norm = normalize(X_num.fillna(0)).dropna(axis=1)  
        constant_filter = VarianceThreshold(threshold=var_tresh)
        constant_filter.fit(X_norm)
        constant_columns = [column for column in X_norm.columns
                        if column not in X_norm.columns[constant_filter.get_support()]]
        X_filtered = X_norm[X_norm.columns[constant_filter.get_support()]]
        
        return X_filtered.columns
0.001
    
    def pre_process_data(self, addr:str):
        """
        Lee los datos preprocesados limpia

        :params str addr: El nombre del archivo incluyendo directorio 
        """
        imp_lista = ['cct', 'semaforo_std',  'anyo_actual','diferencia','edo']
        #Reads csv
        df = pd.read_csv(addr, encoding = 'latin-1')
        print(len(df.columns))
        #df = df[:1000]

        #Drop key variable
        df1 = df.drop(["cambio_std"], axis =1)
        print(len(df1.columns),"Drop")
        
        #Exclude variables with low variance
        imp_vars =  list(set(self.exclude(df1,0.001)) | set(imp_lista))
        df2 = df1[imp_vars]
        print(len(df2.columns),"Exclude low variance")
        
        #First variable selection
        num_vars = floor(sqrt(len(df1.columns)))
        imp_vars =  list(set(self.get_important_variables(df1, num_vars)) | set(imp_lista))
        df3 = df2[imp_vars] 
        print(len(df3.columns),"Var sel")

        #Cleans data
        df4 = self.clean_data(df3)
        print(len(df4.columns),"clean")

        #Removes highly correlated variables
        df5 = self.remove_correlated(df4)
        print(len(df5.columns),"high corr")

        #Second variable selection
        num_vars = 50
        print(num_vars)
        imp_vars =  list(set(self.get_important_variables(df5, num_vars)) | set(imp_lista))

        #Keeps original data with new variables (dirty data)
        #This is so that imputation can be done separetely in train and test sets
        df6 = df1[imp_vars] 
        print(len(imp_vars))
        print(len(df6.columns),"second var sel")

        #Compacts data
        df7 = self.compact_data(df6)
        print(len(df6.columns),"compact")

        return df7
    
    def normalize(dataset):
        dataNorm=((dataset-dataset.min())/(dataset.max()-dataset.min()))
        return dataNorm


    def get_important_variables(self, df, how_many:int):
        """
        Obtiene una lista de variables importantes para todos los estados y 
        considerando todas las diferencias entre años

        :params dataframe df: Características de la escuela y cambios en el tiempo
        """
        estados = list(range(1,34))
        diferencia = list(range(1,6))
        df["edo"] = df.cct.str[:2]
        df["edo"] = pd.to_numeric(df.edo)

        lista_vars = []

        for dif in diferencia:
            df_dif = df[df.diferencia ==dif]

            for edo in estados:
                if edo == 33:
                    df_edo = df_dif
                else:
                    df_edo = df_dif[df_dif.edo ==edo]
                if len(df_edo)>0:
                    X = df_edo.drop(['cct', 'semaforo_std'], axis=1)
                    X_num = X.select_dtypes(include = ['float', 'int']) #Exclude string variables.
                    y = df_edo[['semaforo_std']]
                    X_num.dropna(axis=1, thresh = len(X_num)/4, inplace=True)
                    X_num = X_num.fillna(0)
                    X_train, X_test, y_train, y_test = train_test_split(X_num, y, 
                                                                    test_size=0.15, 
                                                                    random_state=15)
                    #Sort variable importance: Use Random Forest
                    reg_rf = RandomForestClassifier(n_jobs = -1, random_state = 10, oob_score = True, n_estimators = 500) 
                    reg_rf.fit(X_train, y_train)

                    feature_importances = pd.DataFrame(reg_rf.feature_importances_, index = X_train.columns,
                                                      columns=['importance']).sort_values('importance',ascending=False)

                    mean_imp  = np.quantile(feature_importances.importance, 0.65)
                    bench = max(mean_imp, 0.005)
                    nuevas_vars = list(feature_importances[feature_importances.importance >bench].index)

                    union = list(set(lista_vars) | set(nuevas_vars))
                    lista_vars = union
                    print(len(lista_vars))


        return lista_vars







