import requests

try:
    r = requests.get('http://127.0.0.1:3001/')
    print('Status:', r.status_code)
    print('Content-Type:', r.headers.get('Content-Type'))
    print('Content:')
    print(r.text)
except Exception as e:
    print('Error:', e)