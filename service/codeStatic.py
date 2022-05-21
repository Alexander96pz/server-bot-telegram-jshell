import os
import requests
import json
# Making a POST request
def postAnalysis(id_question,code):
    if (len(code) > 0):
        try:
            r = requests.post('http://'+os.getenv("STATIC_KEY")+':8080/script', json={'id': id_question,'code': code})
            # success code - 200
            if(r.status_code == 200):
                # print content of request
                return json.dumps(r.json())
        except Exception:
            print("Error envio analisis estatico")   