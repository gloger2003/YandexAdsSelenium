import requests
from pprint import pprint


pprint(requests.get('http://control-panel123.herokuapp.com/get_user?token=QWE32GH46TW1QU67YHXE3ZXLKT5BNGHUIORWQZX&login=testUser&password=12345').text)

