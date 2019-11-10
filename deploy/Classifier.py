# Librerias
import os
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import f1_score
import pyodbc #Conectar base de datos
import folium #Mapas
from folium import plugins
from folium.plugins import MarkerCluster

class DecreasePerformance:     
    """
    Clase con métodos llamados desde la clase "app.py"
    Tiene los métodos para extraer la tabla de sql, correr clasificadores y crea mapas.
    """

    def get_db(self,  dif=5, lista_estados=[]):
        """ 
        Obtiene tabla de datos desde la base de datos remota

        :param int dif: Los años hacia atrás para predecir el cambio de desempeño escolar
        :param list[int] lista_estados: El indice de los estados  
        :return: Tabla con la información de las escuelas de los estados en
         la lista de estados en el 2013 y "dif" años atrás
        :rtype: dataframe
        """
        running_in=2
        if running_in==3: #Pruebas locales
            temp = os.path.expanduser('C:\\Users\\pmeji\\\Documents\\Tesis\\build\\temp')
            filename= "cambios_2013.csv"
            addr= os.path.join(temp, filename)
            df = pd.read_csv(addr)
            if lista_estados[0]==0:
                df_edo = df
            else:
                df_edo = df[df['edo'].isin(lista_estados)]
            df_res= df_edo[df_edo['diferencia']==dif] 
            
        else:     
            if int(dif) > 0 & int(dif) <6:
                database = 'enlace911'
                username = 'paola'
                password = 'En3r02019'
            
                if running_in == 2:
                    driver = '{ODBC Driver 17 for SQL Server}'
                    server = 'educacion.database.windows.net,1433'
                    cnxn = pyodbc.connect('DRIVER='+driver+';SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+ password)
                elif running_in==1: #Local con SQL
                    driver = '{SQL Server}'
                    server = 'educacion.database.windows.net'
                    cnxn = pyodbc.connect('DRIVER='+driver+';SERVER='+server+';PORT=1433;DATABASE='+database+';UID='+username+';PWD='+ password)

                cond_edos = ""
                tam_lista = len(lista_estados)
                if tam_lista>0 and lista_estados[0]>0:
                    cond_edos = " AND ( edo="
                    for i in range(tam_lista -1):
                        cond_edos = cond_edos + str(lista_estados[i]) + " OR edo = "
                        print(i)
                    cond_edos = cond_edos + str(lista_estados[tam_lista-1]) + " )"

                sql = "SELECT * FROM cambios_2013 WHERE diferencia = " +str(dif) +  str(cond_edos) 
                print(sql)
                df_res = pd.read_sql(sql, cnxn)
                cnxn.close()
        return df_res
    
    def clean_dataset(self, df):
        """ 
        Trata los valores faltantes, valores mayor a infinito, menores a menos infinito para que 
        los datos puedan ser usados para modelar. 

        :param int dif: Los años hacia atrás para predecir el cambio de desempeño escolar
        :return: Las variables independientes númericas (X) y variable dependiente (y)
        :rtype: (dataframe, dataframe)
        """
        assert isinstance(df, pd.DataFrame), "df needs to be a pd.DataFrame"
        X = df.drop(['cct', 'semaforo_std'], axis=1)
        X = X.apply(pd.to_numeric)
        X_num = X.select_dtypes(include = ['float', 'int']) #Exclude string variables.
        X_num.dropna(axis=1, thresh = len(X_num)/4, inplace=True)
        
        #Deals with infinity values
        X_num[X_num==np.inf]=np.nan
        X_num[X_num==-np.inf]=np.nan
        #Deal with missing values
        X_num = X_num.fillna(0)

        #Compress data
        X_num[X_num.select_dtypes(include = ['float64']).columns] \
         = X_num.select_dtypes(include = ['float64']).astype(np.float16)
        X_num[X_num.select_dtypes(include = ['int64']).columns] \
        = X_num.select_dtypes(include = ['int64']).astype(np.int16)
        X_num[X_num.select_dtypes(include = ['float32']).columns] \
        = X_num.select_dtypes(include = ['float32']).astype(np.float16)
        X_num[X_num.select_dtypes(include = ['int32']).columns] \
        = X_num.select_dtypes(include = ['int32']).astype(np.int16)

        X_num = X_num.apply(pd.to_numeric)
        X_num[X_num==np.inf]=np.nan

        indices_to_keep = ~X_num.isin([np.nan, np.inf, -np.inf]).any(1)
        df_new = df[indices_to_keep]
        X_num = X_num[indices_to_keep]

        df_new.reset_index(drop=True, inplace=True)
        X_num.reset_index(drop=True, inplace=True)
        nan_val = X_num.columns[X_num.isna().any()].tolist()
        for vari in nan_val:
            X_num[vari] = X_num[vari].fillna(0)

        y = df_new[['semaforo_std']].astype("int16")
        return y,X_num

    def predict_random_forest(self, df):
        """ 
        Clasifica el desempeño decreciente utilizando un bosque aleatorio, 
        calcula la métrica f1 y extrae las variables más significativas

        :param dataframe df: Tabla con información de las escuelas y una 
        variable indicadora de bajar desempeño
        :return: El valor f1 ponderado de la clasificación, 
        el margen de ganancia del valor f1 comparado con el punto de referencia 
        que es clasificar todas las observaciones
        con la clase mayoritaria
        Una lista con las 10 variables más significativas
        :rtype: float, float, list[str]
        """
        df.dropna(subset=['semaforo_std'],inplace=True)
        df.reset_index(drop=True, inplace=True)
        y, X = self.clean_dataset(df)

        X_train, X_test, y_train, y_test = train_test_split(X, y, 
                                                        test_size=0.15, 
                                                        random_state=15)
        #Sort variable importance: Use Random Forest
        #reg_rf = RandomForestClassifier(n_jobs = -1, random_state = 10, 
                                       # oob_score = True, n_estimators = 100) 
        reg_rf = RandomForestClassifier(random_state = 10, oob_score = True, 
                                        max_depth = 10, n_estimators = 100) 
        reg_rf.fit(X_train, y_train)
        feature_importances = pd.DataFrame(reg_rf.feature_importances_, index = X_train.columns,
                                          columns=['importance']).sort_values('importance',ascending=False)
        nuevas_vars = list(feature_importances.index)[:10]

        y_pred = reg_rf.predict(X_test)
        f1 = f1_score(y_test, y_pred, average='weighted') 

        if ((y_test.sum()/len(y_test))>0.5).bool():
            y_bench = [1]*len(y_test)
        else:
            y_bench = [0]*len(y_test)

        f2 = f1_score(y_test, y_bench, average='weighted') 
        margen= f1-f2
        return f1, margen, nuevas_vars


    def predict_logistic_regression(self, df):
        """ 
        Clasifica el desempeño decreciente utilizando una regresion logística 
        calcula la métrica f1 y extrae las variables más significativas

        :param dataframe df: Tabla con información de las escuelas y una 
        variable indicadora de bajar desempeño
        :return: El valor f1 ponderado de la clasificación, 
        el margen de ganancia del valor f1 comparado con el punto de referencia 
        que es clasificar todas las observaciones
        con la clase mayoritaria
        Una lista con las 10 variables más significativas
        :rtype: float, float, list[str]
        """
        df.dropna(subset=['semaforo_std'],inplace=True)
        df.reset_index(drop=True, inplace=True)
        y, X = self.clean_dataset(df)

        X_train, X_test, y_train, y_test = train_test_split(X, y, 
                                                        test_size=0.15, 
                                                        random_state=15)

        reg_rf = LogisticRegression(C=0.8, max_iter=200) 
        reg_rf.fit(X_train, y_train)

        coefficients = pd.concat([pd.DataFrame(X.columns),pd.DataFrame(np.transpose(reg_rf.coef_))], axis = 1)
        coefficients.columns = ['Variable', 'Coeficiente']
        coefficients= coefficients.sort_values("Coeficiente",ascending=False)
        nuevas_vars = coefficients[:5].append(coefficients[-5:])

        y_pred = reg_rf.predict(X_test)
        f1 = f1_score(y_test, y_pred, average='weighted') 

        if ((y_test.sum()/len(y_test))>0.5).bool():
            y_bench = [1]*len(y_test)
        else:
            y_bench = [0]*len(y_test)

        f2 = f1_score(y_test, y_bench, average='weighted') 
        margen= f1-f2
        return f1, margen, nuevas_vars

    def edit_name(self, nombre):
        nota = ""
        if(nombre!="p_mat_anterior"):
            if nombre.startswith("a_"):
                nombre = nombre[2:]
                nota= nota + "Variable del periodo anterior. " 
            if nombre.startswith("p_"):
                nombre = nombre[2:]
                nota = nota + "Propoción entre la variable del periodo anterior y la variable del periodo actual. " 
            if nombre.startswith("dif_"):
                nombre = nombre[4:]
                nota= nota + "Diferencia entre la variable del periodo anterior y la variable del periodo actual."
        return nombre, nota

    def get_table(self, nuevas_vars):
        """ 
        Da formato a tabla de variables significativas del modelo para poder 
        desplegarlas en la aplicación. Obtiene la descripción de las variables

        :param list[str] nuevas_vars: Lista de las 10 variables más 
        significativas después de la clasifición
        :return: Un dataframe con el nombre de las variables y la descripción
        :rtype: dataframe
        """
        descripcion = pd.read_csv("./data/variables_generadas.csv")

        nuevas_vars["Base"] =""
        nuevas_vars["Notas"]= ""

        nuevas_vars.reset_index(drop=True, inplace=True)
        tam = len(nuevas_vars)
        for i in range(tam):
            base, notas= self.edit_name(nuevas_vars["Variable"][i])
            nuevas_vars["Base"][i] =base
            nuevas_vars["Notas"][i] =notas


        junto = nuevas_vars.merge(descripcion, left_on="Base", right_on="Nombre de variable")
        presenta_info = junto[["Variable", "Coeficiente", "Descripcion", "Notas"]]
        presenta_info.Coeficiente = presenta_info.Coeficiente.round(2) 
        return presenta_info
    
    def get_results(self, dif, lista_estado):
        """ 
        Es la función "Main", llama a las otras funciones y regresa los 
        valores a la clase App. 

        :param int dif: Los años hacia atrás para predecir el cambio de 
        desempeño escolar
        :param list[int] lista_estados: El indice de los estados 
        :return: El valor f1 ponderado de la clasificación, 
        el margen de ganancia del valor f1 comparado con el punto de referencia 
        que es clasificar todas las observaciones
        con la clase mayoritaria
        Una lista con las 10 variables más significativas 
        Una base con codigo de la escuela y la variable objetivo que se 
        utilizará para construir el mapa
        :rtype: float, float, list[str], dataframe
        """
        df = self.get_db(dif, lista_estado)
        f1, margen, nuevas_vars = self.predict_logistic_regression(df)
        tabla_vars = self.get_table(nuevas_vars)
        return f1, margen, tabla_vars, df[['cct','semaforo_std']]


    def get_map(self, df_escuelas,name):
        """ 
        Construye un mapa con máximo 100 escuelas donde el
        color indica si baja desempeño (rojo) o no (verde).

        :param dataframe df_escuelas: Las claves de las escuelas
        y la variable objetivo

        :param str name: Nombre que se le da al mapa
        :return: El valor f1 ponderado de la clasificación, 
        el margen de ganancia del valor f1 comparado con el punto de referencia 
        que es clasificar todas las observaciones
        con la clase mayoritaria
        Una lista con las 10 variables más significativas 
        Una base con codigo de la escuela y la variable objetivo que se 
        utilizará para construir el mapa
        :rtype: float, float, list[str], dataframe
        """
        #Falta ver si se puede subir
        df_lat = pd.read_csv('data/escuelas_latlon.csv', encoding = 'latin-1')

        df =  pd.merge(df_escuelas, df_lat, on='cct' )

        cen_lon = df.longitud.mean()
        cen_lat = df.latitud.mean()

        mapi = folium.Map(location=[cen_lat,cen_lon],
                            zoom_start = 6,
                        tiles="cartodbpositron")

        df.reset_index(drop=True, inplace=True)
        df = df.sort_values("semaforo_std", ascending= False)
        df = df[:100]
        df.reset_index(drop=True, inplace=True)

        for col in range(len(df)):
            lon = df["longitud"][col]
            lat = df['latitud'][col]
            nombre = df["cct"][col]
            valor = df['semaforo_std'][col]
            
            if int(valor) > 0:
                color_sch = 'red'
                fill_sch = 'orange'
            else:
                color_sch = 'green'
                fill_sch = 'yellow'

            folium.features.CircleMarker(
            location=[lat,lon],
            popup=nombre,
            color=color_sch,
            fill_color = fill_sch,
            fill_opacity=0.2
            ).add_to(mapi)

        mapi.save(name)