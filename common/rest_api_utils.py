import requests

def get_request(url, headers):
    '''
    A function to perform a GET request.

    Args:
        url (string): The URL of API call
        headers (dictionary): The dictionary of headers

    Returns:
        string: The response from call

    Raises:

    '''

    response = requests.get(url, headers=headers, verify=False)
    return response


def post_request(url, data, headers):
    '''
    A function to perform a POST request.

    Args:
        url (string): The URL of API call
        data (dictionary): The data to use on API call
        headers (dictionary): The dictionary of headers

    Returns:
        string: The response from call

    Raises:

    '''

    response = requests.post(url, data=data, headers=headers)
    return response


def delete_request(url, headers):
    '''
    A function to perform a DELETE request.

    Args:
        url (string): The URL of API call
        data (dictionary): The data to use on API call
        headers (dictionary): The dictionary of headers

    Returns:
        string: The response from call

    Raises:

    '''

    response = requests.delete(url, headers=headers)
    return response
