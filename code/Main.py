import os

from Cleaning import CleanData
from Modelling import BuildModels

class Principal():
    
    #GLOBALS
    SERVIDOR = os.path.expanduser('C:\\Users\\pmeji\\\Dropbox\\ITAM\\OctavoSemestre\\PredecirDesempeno')
    TEMP = os.path.expanduser('C:\\Users\\pmeji\\\Documents\\Tesis\\build\\temp')
    
    modelador = BuildModels()
    limpiador = CleanData()
    
    
    def limpia(self, addr, guarda):
        
        df_processed = limpiador.process_data(addr)
        df_processed.to_csv(gurada, index =False)
        print("Archivo guardado")
        
        
    def modela(self, addr):

        df = pd.read_csv(addr)
        #df = df[:100]

        df['edo'] = df.cct.str[:2]
        df["edo"] = pd.to_numeric(df.edo)
        df_new = limpiador.clean_data(df)

        optimal, results, info_params = modelador.get_models_metrics(df_new)
        pd.DataFrame(results).to_csv("results.csv", index =False)
        pd.DataFrame(optimal).to_csv("optimal.csv", index =False)
        pd.DataFrame(info_params,  index =[1]).to_csv("params.csv", index =False)

        ganancia_orig, benchmark_orig, resultados_orig = modelador.resultados_por_estado(df_new)
        pd.DataFrame(ganancia_orig).to_csv("ganancia_final.csv", index =False)
        pd.DataFrame(benchmark_orig).to_csv("benchmark_final.csv", index =False)
        pd.DataFrame(resultados_orig).to_csv("resultados_final.csv", index =False)
    
    
    def main(self):
        
        filename= "cambios_a_2_cemabe_2013.csv"
        addr= os.path.join(SERVIDOR, filename)
        filename= "cambios_2013.csv"
        guarda= os.path.join(TEMP, filename)    
        self.limpia(addr,guarda)
        
        filename= "cambios_2013.csv"
        addr= os.path.join(TEMP, filename)
        self.modela(addr)
                
    
if __name__ == '__main__':
    main()
