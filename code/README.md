# Diseño e implementación de un producto de datos para la toma de decisiones en programas sociales para escuelas primarias en México

## Acerca del proyecto
El objetivo de la aplicación es proporcionar información para la toma de decisiones de politicas públicas y asignación de programas sociales educativos en primarias de México. La aplicación genera criterios de riesgo de desempeño escolar para identificar cuáles escueles tienen bajo desempeño y por qué. Mientras más alta sea la calificación, peor es el desempeño de la escuela.      

## Así que, ¿cómo funciona?
Al seleccionar estados y tipo de escuela, la aplicación clasifica las escuelas utilizando una regresión bernouli con liga logística. 

## Sobre los archivos de este repositorio
* Preprocessing.do: Lee los archivos, crea variables de interaccion y de cambio
* Cleaning.py: Tiene los archivos para limpiar y seleccionar los datos
* Modelling.py: Crea y evalúa los modelos
* Classifier.py: Archivo principal usado en la aplicación

 
