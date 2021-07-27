import requests
from pprint import pprint



pprint(requests.get('http://control-panel123.herokuapp.com/get_user?login=Vlad&password=123545').json())