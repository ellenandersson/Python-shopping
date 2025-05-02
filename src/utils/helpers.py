def send_request(url, method='GET', data=None, headers=None):
    import requests

    if method.upper() == 'GET':
        response = requests.get(url, headers=headers)
    elif method.upper() == 'POST':
        response = requests.post(url, json=data, headers=headers)
    else:
        raise ValueError("Unsupported HTTP method: {}".format(method))

    response.raise_for_status()
    return response


def parse_response(response):
    from bs4 import BeautifulSoup

    soup = BeautifulSoup(response.text, 'html.parser')
    return soup