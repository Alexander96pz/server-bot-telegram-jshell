from re import L
import docker
import time
import threading
import registry_credentials
import re

MESSAGE_LIMIT = 4096

def launch(lang, pipeout, on_close,id_question):
    return Repl(lang, pipeout, on_close,id_question)

def pipein(instance, text, message):
    instance.pipein(text,message)

def kill(instance):
    instance.kill()

def next(instance):
    instance.NextQuestion()
# metodo para limpiar mensajes de salida del REPL
def cleanResponse(listas):
    for l in listas:
        # Eliminamos los mensajes iniciales del REPL
        if l.find("Welcome to JShell") != -1:
            listas = []
    return listas

def validateError(lines):
    validate=False
    validate1=False
    validate2=False
    for l in lines:
        if l.find("Error:") != -1:
            validate1=True
        if l.find("^") != -1:
            validate2=True
    if validate1 == True and validate2 == True:
        validate=True
    return validate

class Repl:
    def __init__(self, lang, pipeout, on_close,id_question):
        # Genera un contenedor con el intérprete para el idioma dado.
        # Devuelve una instancia del contenedor.
        # pipeout es una función que toma una cadena y la envía de vuelta al usuario.
        # Úsada para enviar salida estándar desde el contenedor.
        self.client = docker.APIClient()
        self.on_close = on_close
        self.lang = lang
        self.text = ''
        self.id_user = 0
        self.id_message=0
        self.id_question=id_question
        # Language seleccion
        if lang == "java":
            self.container = self.client.create_container(
                image = "java-repl",
                stdin_open = True,
                detach = True,
                tty = False
            )
        # Inicializo the container
        self.client.start(self.container)
        # Get sockets
        self.input = self.client.attach_socket(self.container, params={'stdin': 1, 'stream': 1})._sock
        self.output = self.client.attach_socket(self.container, params={'stdout': 1, 'stream': 1})._sock
        # Inicializo listener
        self.listener = threading.Thread(target = self.__listen, args = [pipeout])
        self.listener.start()

    def pipein(self, text, message):
        # Envía la cadena de texto al contenedor como entrada estándar.
        # No devuelve nada.
        self.id_message=message.id_message
        self.id_user = message.fk_id_user
        self.text=text
        self.input.send(text.encode('utf-8')) # Convercion a bytes
    # Parar un contenedor
    def kill(self):
        self.client.stop(self.container) # Elimino/Stop el contenedor

    # RESPUESTA del REPL
    def __listen(self, pipeout):
        # obtengo las salidas o registros(logs) del contenedor
        logs = self.client.logs(
            self.container,
            stdout = True,
            stream = True
        )
        lines=[]
        for line in logs:
            # transformo de bytes a string
            decode_line=line.decode('utf-8')
            # si la linea esta vacia
            if len(decode_line) == 1:
                isError=validateError(lines)
                out=cleanResponse(lines)
                lines=[]
                # if isError:
                #     self.id_question +=1
                pipeout(out,isError,self.text,self.id_user,self.id_message,self.id_question)
            else:
                lines.append(decode_line)
        # Una vez que se alcanza este código, el contenedor está muerto
        self.on_close()
        self.client.remove_container(self.container) # elimino el container
    
    def NextQuestion(self):
        self.id_question+=1

    # def setQuestion(self,question):
    #     self.id_question=question
    # def getQuestion(self):
    #     return self.id_question