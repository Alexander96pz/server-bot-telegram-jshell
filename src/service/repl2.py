import docker
import time
import threading
# import registry_credentials

MESSAGE_LIMIT = 4096
def cleanResponse2(listas):
    lista2=[]  # lista auxiliar
    for l in listas:
        if l.find("Welcome to JShell") != -1:
            listas = ["Puedes Programar"]
            return listas
        lista2.append(l)
    listas = lista2
    return listas

def launch2(lang, pipeout, on_close):
    return Repl2(lang, pipeout, on_close)


def pipein2(instance, text):
    instance.pipein(text)


def kill(instance):
    instance.kill()


class Repl2:
    def __init__(self, lang, pipeout2, on_close2):
        """
        Spawns a container with the interpreter for the given language.
        Returns an instance of the container.
        pipeout is a function that takes a string and sends it back to the user.
        Use it to send standard output from the container.
        """
        self.client = docker.APIClient()

        self.on_close = on_close2
        self.lang = lang

        # Language selection
        if lang == "java":
            self.container = self.client.create_container(
                image="java-repl",
                stdin_open=True,
                detach=True,
                tty=False
            )
        # Start the container
        self.client.start(self.container)

        # Get sockets
        self.input = self.client.attach_socket(self.container, params={'stdin': 1, 'stream': 1})._sock
        self.output = self.client.attach_socket(self.container, params={'stdout': 1, 'stream': 1})._sock

        # Initialise listener
        self.listener = threading.Thread(target=self.__listen, args=[pipeout2])
        self.listener.start()

    def pipein(self, text):
        """
        Sends the text string into the container as standard input.
        There is no need to return anything.
        """
        self.input.send(text.encode('utf-8'))  # Convert to bytes

    def kill(self):
        self.client.stop(self.container)  # Stop the container

    def __listen(self, pipeout2):
        logs = self.client.logs(
            self.container,
            stdout=True,
            stream=True
        )
        lines = []
        for line in logs:
            decode_line = line.decode('utf-8')
            if len(decode_line) == 1:
                out = cleanResponse2(lines)
                # if len(out) != 0:
                lines = []
                pipeout2("".join(out))
            else:
                lines.append(decode_line)

        # Once this code is reached, the container is dead
        self.on_close()
        self.client.remove_container(self.container)  # Remove the container
