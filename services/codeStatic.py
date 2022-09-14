import logging
import os
import requests
import json
# Conexion al servidor de Analisis Estatico
# Making a POST request
def postAnalysis(id_question, code, prerequisites, posrequisites, valor, console):
    if (len(code) > 0):
        try:
            r = requests.post('http://'+os.getenv("STATIC_KEY")+':8080/script',
                              json={'id': id_question,
                                    'code': code,
                                    'prerequisites': prerequisites,
                                    'posrequisites': posrequisites,
                                    'valor': valor,
                                    'console':console,
                                    }
                              )
            # success code - 200
            if(r.status_code == 200):
                # print content of request
                responseAnalyst = json.dumps(r.json())
                if responseAnalyst:
                    responseAnalyst = json.loads(responseAnalyst)
                    if ('REJECTED' == responseAnalyst["status"]):
                        return True
                    else:
                        return False
        except Exception:
            logging.ERROR("Error send comunication with server analysis static")
