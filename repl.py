import docker
import time
import threading
import registry_credentials

MESSAGE_LIMIT = 4096

def launch(lang, pipeout, on_close):
    return Repl(lang, pipeout, on_close)

def pipein(instance, text):
    instance.pipein(text)

def kill(instance):
    instance.kill()

class Repl:
    def __init__(self, lang, pipeout, on_close):
        # Genera un contenedor con el intérprete para el idioma dado.
        # Devuelve una instancia del contenedor.

        # pipeout es una función que toma una cadena y la envía de vuelta al usuario.
        # Úsada para enviar salida estándar desde el contenedor.

        self.client = docker.APIClient()

        self.on_close = on_close
        self.lang = lang

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

    def pipein(self, text):
        # Envía la cadena de texto al contenedor como entrada estándar.
        # No es necesario devolver nada.
        self.input.send(text.encode('utf-8')) # Convercion a bytes

    def kill(self):
        self.client.stop(self.container) # Elimino/Stop el contenedor

    def __listen(self, pipeout):
        logs = self.client.logs(
            self.container,
            stdout = True,
            stream = True
        )
        if self.lang == "python": # Python REPL descarga stdout después de cada carácterr
            sb = []
            for line in logs:
                decoded_line = line.decode('utf-8')
                # Solo canalización en nueva línea
                if '\n' in decoded_line:
                    pipeout(''.join(sb))
                    sb = []
                else:
                    sb.append(decoded_line)
        else:
            for line in logs:
                pipeout(line.decode('utf-8'))
        
        # Una vez que se alcanza este código, el contenedor está muerto
        self.on_close()
        self.client.remove_container(self.container) # elimino el container
