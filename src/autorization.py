from uuid import uuid4

import requests


def authorize(scope: str, auth_key: str):
    auth_key = auth_key.strip('\"').strip('\'')
    scope = scope.strip('\"').strip('\'')

    url = 'https://ngw.devices.sberbank.ru:9443/api/v2/oauth'
    payload = {
        'scope': scope
    }
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': 'application/json',
        'RqUID': str(uuid4()),
        'Authorization': f'Basic {auth_key}'
    }

    response = requests.post(
        url,
        headers=headers,
        data=payload,
        verify=False
    )

    return response.json()['access_token']
