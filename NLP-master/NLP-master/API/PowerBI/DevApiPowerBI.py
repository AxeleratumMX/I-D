import flask
from flask import request, jsonify
import requests
import json

# =============================================================================
# Estos son los id de los dataset para actualizar.
# =============================================================================
viva = "9b115bd1-de84-4cc1-b622-404d685ceb03"
test = "7432750a-d945-455c-b40d-d858e962d586"
testapi = "758736ca-1910-4cd2-a143-ff10cb40972e"
# =============================================================================
# A continuación se ejecuta la función get_token() para obtener el access token
# de azure y con esto tener acceso a la API de Power BI, al ejecutarse actualiza
# el anterior token el cual tiene una duración de 60 minutos.
# =============================================================================
def get_token():
    link= "https://login.windows.net/common/oauth2/token"
    form = {
            'client_secret': 'Qcrt1aDs3xz4i31yMTE8lBYNJ+uqAfgku0ekjSitsow=',
            'client_id': '3e0e899e-7051-47df-9b15-aca1cfed2dbc',
            'grant_type': 'password',
            'resource': 'https://analysis.windows.net/powerbi/api',
            'username': 'ruben@axeleratum.com',
            'password': 'L4n14k3a'
            }
    headers = {'Content-type': 'application/x-www-form-urlencoded'}
    respuesta = requests.post(url = link, headers = headers, data = form)
    
    res= respuesta.json()
    #print(res)
    token = res['access_token']
    return token


app = flask.Flask(__name__)
app.config["DEBUG"] = False

@app.route('/', methods=['GET'])
def home():
    return '''<h1>API PowerBI</h1>
<p>API para refresh de datasets en Power BI</p>'''


# =============================================================================
# Endpoint /refreshdataset realiza el llamado a la API de Power bi para
# efectuar la actualización del dataset
# =============================================================================
@app.route('/api/v1/powerbi/refreshdataset', methods=['PUT'])
def dataset_refresh():
    global status
    endpoint_refresh = "https://api.powerbi.com/v1.0/myorg/datasets/"+testapi+"/refreshes"
    headers = {'content-type': 'application/json', 'Authorization': 'Bearer '+ get_token()}
    send = requests.post( url = endpoint_refresh, headers= headers)
   #print(get_token())
    #print(send)
    code = send.status_code
    print(code)
    #estado = status(code)
    #print(estado)
    status = {'code':code}
    jsonify(status)
    return status

@app.errorhandler(404)
def page_not_found404(e):
    return "<h1>404</h1><p>The resource could not be found.</p>", 404

@app.errorhandler(500)
def page_not_found500(e):
    return "<h1>404</h1><p>The resource could not be found.</p>", 500

# =============================================================================
# Definicón de los códigos que regresa la API de Power BI
    '''! Tiene error de formato aún no resuelto'''
# =============================================================================
def status(code):
    global resp
    if code == 400:
        resp = "Invalid dataset refresh request. Another refresh request is already executing"
    elif code == 403:
        resp = "Access forbidden"
    elif code == 202:
        resp = "Accepted, refreshing dataset: " + testapi
    return resp

app.run()