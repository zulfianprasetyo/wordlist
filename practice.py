import requests

api_key = 'bc8985cf-3de7-4e8d-b593-d3decfc9c093'
word = 'voluminous'
url = f'https://www.dictionaryapi.com/api/v3/references/collegiate/json/{word}?key={api_key}'

r = requests.get(url)

results = r.json()

for result in results:
    print(result)