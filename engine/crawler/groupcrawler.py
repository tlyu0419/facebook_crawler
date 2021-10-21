import requests
url = 'https://www.facebook.com/groups/pythontw'

rs = requests.session()
headers = {}
resp = rs.post(url, )
resp.text[:5000]