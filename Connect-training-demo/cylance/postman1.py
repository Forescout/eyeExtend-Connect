# test postman server

import requests

url = "https://ec2651a8-de64-4f6c-a8a2-88793613c678.mock.pstmn.io/pollock"

headers = {
    'x-api-key': "PMAK-5e1d087805d30d0037c17580-2c7e30c47d6925b5ca3019f8bb122a8840",
    'User-Agent': "PostmanRuntime/7.20.1",
    'Accept': "*/*",
    'Cache-Control': "no-cache",
    'Postman-Token': "d855aed7-5b32-4262-ae26-e13f2371e14f,b374b967-c169-415b-8796-5ff5dd91f517",
    'Host': "ec2651a8-de64-4f6c-a8a2-88793613c678.mock.pstmn.io",
    'Accept-Encoding': "gzip, deflate",
    'Connection': "keep-alive",
    'cache-control': "no-cache"
    }

response = requests.request("GET", url, headers=headers)

print(response.text)
