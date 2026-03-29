import requests

try:
    r = requests.get('http://127.0.0.1:3002/')
    print('Status:', r.status_code)
    print('Content-Type:', r.headers.get('Content-Type'))
    print('Headers:')
    for k, v in r.headers.items():
        print(f'  {k}: {v}')
    print('\nContent (first 500 chars):')
    print(r.text[:500])
except Exception as e:
    print('Error:', e)