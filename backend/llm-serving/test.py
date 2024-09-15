from sgl_vlm import Model
import requests

model = Model()
image_url=None
question=None
response = requests.post(
    "https://xpbowler--hackmit-model-generate.modal.run",
    json={
        "image_url": image_url,
        "question": question,
    },
)
print(response.json().get('answer',None))