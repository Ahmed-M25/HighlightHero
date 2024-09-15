from sgl_vlm import Model
import requests

model = Model()
question="Narrate this video as if you were a sports commentator."
response = requests.post(
    "https://xpbowler--hackmit-model-generate.modal.run",
    json={
        "question": question,
    },
)

print(response.json().get('answer',None))