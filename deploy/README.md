# Aplicación web para distribuir producto de datos

La estrategia para la distribución fue a través de una aplicación web.
Las ventajas de las aplicaciones web es que pueden ser accedidas desde cualquier lugar geográfico con internet y un navegador. De esta forma se pretende que el proyecto tenga mayor alcance. 

La aplicación web permite a los usuarios hacer consultas para estados y diferencia de periodo en específico. De forma que los usuarios pueden realizar las siguientes operaciones:
* Seleccionar los estados y el periodo de tiempo del cual desee obtener información
* visualizar en un mapa las escuelas con rendimiento decreciente
* Obtener la clave de la escuela al dar click sobre un punto en el mapa
* Descargar una lista con clave de la escuela y su clasificación
* Visualizar las variables más significativas con sus coeficientes
* Visualizar el número de observaciones y el valor $F_1$ de la clasificación


## Aplicación web
Se construyó la aplicación Web utilizando la herramienta ``Dash''. Dash es un entorno de trabajo de Python que está basado en Flask y React. Se escogió este entorno de trabajo por la facilidad de implementar el código previamente escrito en Python de creación de mapas y de aprendizaje de máquina como el bosque aleatorio para la limpieza de datos y modelos de Regresión Logística.

Para la construcción de la aplicación se genero un archivo "Classifier.py" con los métodos de limpieza y de modelado y el archivo principal "app.py" que llama a los métodos y despliega el mapa, las tablas y el menú.

## Alojamiento web
Para el despligue existen varías alternativas, entre ellas utilizar plataformas como Amazon Web Services, Microsoft Azure o Heroku. En un principio se eligió utilizar Heroku por su facilidad de vincular la aplicación con un repositorio de Github. Sin embargo, en Heroku corren las aplicaciones sobre una máquina Linux sin opción de hacer grandes modificaciones al entorno. Por esa razón, se optó por hacer el despligue en Microsoft Azure desde un contenedor de Docker. 

Se construyeron dos imágenes de Docker. Docker es una plataforma para el desarrollo, migración y ejecución de aplicaciones utilizando la tecnología de virtualización de contenedores. Utilizando un archivo Dockerfile es posible crear nuevas imágenes que son utilizadas para crear contenedores.

La primera imagen (paolamedo/dash-sql-azure) está construida sobre una máquina Ubuntu versión 16. Una de las mayores complicaciones del despliegue fue acceder a un servidor SQL de Microsoft desde Ubuntu. Para esto fue necesario instalar drivers y programas especiales como mssql. La instalación de programas, drivers y aplicaciones como Python es tardada y puede ser utilizada en muchos otros proyectos por eso se eligió separarla del código de este proyecto.

La segunda imagen (paolamedo/sql-azure) está construida sobre la primer imágen y agrega los archivos específicos del proyecto. Asimismo, expone el puerto 8050 (sobre el cual corre la aplicación de Dash) y automáticamente empieza la aplicación. 

La ventaja de tener ambas imágenes es que cualquier cambio en el código solo modifica la segunda imagen que se construye en poco tiempo. Ambas imágenes se construyeron de forma local y una vez probadas fueron agregadas a DockerHub, una biblioteca en línea de imágenes. 

Finalmente, se creo una aplicación web en Microsoft Azure y se vinculó con la imagen paolamedo/sql-azure. La aplicación se actualiza automáticamente cuando la imagen se actualiza. Al igual que en la construcción de la imágen, fue necesario exponer el puerto 8050 para poder acceder a la aplicacipon. Se escogió un plan de aplicación con 1 GB de memoria y 60 minutos de computo al día por restricción presupuestal. Sin embargo, es posible mejorar la velocidad y memoria en cualquier momento.    