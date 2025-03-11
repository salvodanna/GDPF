import requests

proxies = {
    'http':'socks5://127.0.0.1:9050',
    'https':'socks5://127.0.0.1:9050'
}

print(requests.get('https://ident.me').text)

print(requests.get('https://ident.me', proxies=proxies).text)