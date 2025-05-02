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

    # Check if response is already a string or a response object
    if hasattr(response, 'text'):
        html_content = response.text
    else:
        html_content = response  # Assume it's already a string

    soup = BeautifulSoup(html_content, 'html.parser')
    return soup
