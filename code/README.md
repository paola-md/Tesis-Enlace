# Codigos 

## Acerca del proyecto
El objetivo de la aplicación es proporcionar información para la toma de decisiones de politicas públicas y asignación de programas sociales educativos en primarias de México. La aplicación pretende responder la pregunta: ¿Cuáles escuelas primarias están en riesgo de bajar su rendimiento académico?. Asimismo, se pretende que el usuario tenga la flexibilidad de escoger los estados de interés y el tiempo a futuro. Un año hacia adelante predice el resultado en el corto plazo y cinco años hacia adelante en el largo plazo.     

## Así que, ¿cómo funciona?
Al seleccionar estados y tipo de escuela, la aplicación clasifica las escuelas utilizando una regresión Bernoulli con liga logística. 

## Sobre los archivos de este repositorio
* Preprocessing.do: Lee los archivos, crea variables de interaccion y de cambio
* Cleaning.py: Tiene los archivos para limpiar y seleccionar los datos
* Modelling.py: Crea y evalúa los modelos
* Classifier.py: Archivo principal usado en la aplicación


