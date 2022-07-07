# server-bot-telegram-jshell

Este sistema propone desarrollar un chatbot que permita a los estudiantes de cursos de programación evaluar sus progresos en lo que ha escritura de programas se trata
, es decir el chatbot planteará preguntas cuyas respuestas deben ser líneas de código, que no serán seleccionadas de varios opciones, 
sino escritas por usuario. De esta forma se puede evaluar las capacidades de un estudiante en niveles de conocimiento de categorías superiores. 



## Background

El trabajo debe evaluar la factibilidad del desarrollo de este tipo de iniciativas (escribir programas), desde 
diferentes aristas, partiendo de la usabilidad, pasando por temas de la evaluación de respuestas, también 
seguridad que no se ejecute código malicioso, hasta llegar temas como el registro de información para su 
posterior explotación. Una vez hechas las evaluaciones se debe desarrollar un prototipo para el lenguaje de 
programación Java utilizando Telegram

Objetivo: Implementar un prototipo de chatbot, para el lenguaje Java en Telegram, para que 
los usuarios pueden escribir programas o fragmentos como respuesta a una interrogante

Para realizar el analisis de codigo usamos la herramienta: 

* JShell (Java)

### Prerequisites

* Python 3.8.0
* pip3

```
$sudo apt-get install python3.8
$sudo apt-get install python3-pip
```
* Docker [install](https://docs.docker.com/engine/install/ubuntu/).
Es necesario tener instalado docker

### Installing

Clona el repositorio.
```
$git clone https://github.com/Alexander96pz/server-bot-telegram-jshell.git
$cd server-bot-telegram-jshell
```
Instala los requerimientos
```
pip install -r requirements.txt
```
Construye las imagenes
```
$docker build -t base -f dockerfiles/base-dockerfile .
$docker build -t java -f dockerfiles/java-dockerfile .
$docker build -t alexander96pz/java-repl -f dockerfiles/java-repl-dockerfile .
```
Levanta el servidor Chatbot
```
python src/main
```
Finalmente instala y levanta el servidor encargado del analisis estatico [enlace](https://github.com/Alexander96pz/server-sandbox.git)
