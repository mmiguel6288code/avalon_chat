import requests, pickle
with open('token.pcl','rb') as f:
    token_response = pickle.load(f)
token_data = token_response.json()
access_token = token_data['access_token']
api_base_url = 'https://api.zoom.us/v2/'

def get(api_request,access_token=access_token,api_base_url=api_base_url):
    url = api_base_url + api_request
    r = requests.get(url,headers={'authorization':'Bearer ' + access_token})
    if 200 <= r.status_code < 300:
        pass
    else:
        raise Exception(str(r.status_code) + ' ' + r.text)
    return r
def post_json(api_request,json,access_token=access_token,api_base_url=api_base_url):
    url = api_base_url + api_request.lstrip('/')

    r = requests.post(url,json=json,headers={'Content-Type':'application/json','authorization':'Bearer ' + access_token})
    if 200 <= r.status_code < 300:
        pass
    else:
        raise Exception(str(r.status_code) + ' ' + r.text)
    return r
if __name__ == '__main__':
    import os
    os.environ['PYTHONINSPECT'] = '1'

