import docker
import threading
import services.codeStatic as ca
from models.answer import Answer
import logging

MESSAGE_LIMIT = 4096

def launch(lang, pipeout, on_close,question,nro_tried):
    return Repl(lang, pipeout, on_close,question,nro_tried)

def pipein(instance, text, message):
    try:
        instance.pipein(text,message)
    except Exception:
        logging.ERROR("error pipein")
async def kill(instance):
    instance.kill()

def next(instance,question):
    instance.NextQuestion(question)

def next_tried(instance):
    instance.setTried()
def get_tried(instance):
    return instance.getTried()

# metodo para limpiar mensajes de salida del REPL
def cleanResponse(text,listas):
    for l in listas:
        if l.find("Welcome to JShell") != -1:
            listas = []
            return listas
    lista2=[]  # lista auxiliar
    if(text[-2:].find(";") != -1):
        text=text[:-2]
    else:
        text=text[:-1]
        pass
    for l in listas:
        if(l.find(text) != -1):
            lista2.append(l.replace(text,""))
        else:
            lista2.append(l)
    if(lista2[0].find("|  Error:") != -1):
        linea=lista2[0]
        num=lista2[0].find("|")
        lista2[0] = linea[num:]
    listas = lista2
    return listas

# Interpretacion de Resultados / Analisis Dinamico
def validateError(lines):
    validate1=False
    validate2=False
    if len(lines) == 0:
        return True
    else:
        for l in lines:
            if l.find("Error:") != -1:
                validate1=True
            if l.find("^") != -1:
                validate2=True
        if validate1 == True and validate2 == True:
            return True
        else:
            return False
class Repl:
    def __init__(self, lang, pipeout, on_close,question,nro_tried):
        # Devuelve una instancia del contenedor.
        # pipeout es una función que toma una cadena y la envía de vuelta al usuario.
        # Úsada para enviar salida estándar desde el contenedor.
        self.client = docker.APIClient()
        self.on_close = on_close
        self.lang = lang
        self.text = ''
        self.snippet = ''
        self.id_user = 0
        self.id_message = 0
        self.id_question = question.id_question
        self.prerequisites = question.prerequisites
        self.posrequisites = question.posrequisites
        self.nro_tried = nro_tried
        self.valor = question.valor
        self.console = question.console
        # Language seleccion
        if lang == "java":
            self.container = self.client.create_container(
                image = "alexander96pz/java-repl",
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
        # stop el entorno/contenedor automaticamente 1 hora
        self.temporizer_container = threading.Timer(3600,self.on_close)
        self.temporizer_container.start()


    def pipein(self, text, message):
        # Envía la cadena de texto al contenedor como entrada estándar.
        # No devuelve nada.
        self.id_message=message.id_message
        self.id_user = message.fk_id_user
        self.snippet = text
        if(self.prerequisites is None):
            self.text = text
        else:
            self.text = self.prerequisites+text
        if(self.posrequisites is None):
            pass
        else:
            self.text = self.text+self.posrequisites
        self.text += '\n'
        self.input.send(self.text.encode('utf-8')) # Convercion a bytes
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
                    out=cleanResponse(self.text,lines)
                    # interpretacion de la respuesta del analisis dinamico
                    analysis_dynamic=validateError(out)
                    answer = None
                    analysis_static=True
                    # si no hay erroresen el analisis dinamico
                    if not analysis_dynamic:
                        # if error en el analisis estatico True else False
                        try:
                            analysis_static = ca.postAnalysis(self.id_question, self.snippet, self.prerequisites, self.posrequisites, self.valor, self.console)
                        except Exception:
                            logging.ERROR("Problems with the server of Analysis Static")
                    if len(out) != 0:
                        try:
                            answer = Answer.add_Answer("".join(out),analysis_dynamic, analysis_static)
                        except:
                            logging.error('Error save answer to the DB')
                    lines = []
                    try:
                        pipeout(out,self.id_user,self.id_message,self.id_question,self.nro_tried,answer)
                    except:
                        logging.ERROR("Error en la envio del pipeout")
            else:
                lines.append(decode_line)
        # Una vez que se alcanza este código, el contenedor está muerto
        self.on_close()
        self.client.remove_container(self.container) # elimino el container

    def NextQuestion(self,question):
        if question is None:
            pass
        else:
            self.id_question=question.id_question
            self.prerequisites = question.prerequisites
            self.posrequisites = question.posrequisites
            self.valor = question.valor
            self.console = question.console