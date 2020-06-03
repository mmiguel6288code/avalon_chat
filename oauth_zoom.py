import requests, pickle, webbrowser
from base64 import b64encode
from flask import Flask, redirect, request
app = Flask(__name__)

from config import client_id, client_secret, authorize_url, port

@app.route('/')
def main():
    return redirect(authorize_url,code=302)

@app.route('/token')
def token():
    code = request.args.get('code')
    r = requests.post('https://api.zoom.us/oauth/token',
            data={
                'grant_type':'authorization_code',
                'code':code,
                'redirect_uri':'http://localhost:5000/token',
                },
            headers={
                'Authorization':'Basic '+ b64encode((client_id+':'+client_secret).encode()).decode()
                }
            )
    if r.status_code == 200:
        with open('token.pcl','wb') as f:
            pickle.dump(r,f)
        return 'Successfully obtained new token. Kill authentication server and run application'

    else:
        print(r)
        print(r.text)
        return str(r.status_code) + ' ' + r.text

if __name__ == '__main__':
    webbrowser.open('http://localhost:'+str(port))
    app.run(host='0.0.0.0',port=port)
