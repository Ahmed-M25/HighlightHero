import requests

url = "https://xpbowler--hackmit-model-generate.modal.run"
file_path = './resources/dog.mp4'
files = {'file': open(file_path, 'rb')}

response = requests.post(url, files=files)

print(response.json().get('answer',None))