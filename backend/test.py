from sgl_vlm import Model
import requests

model = Model()
prompt="Narrate this video as if you were a sports commentator."
response = requests.post(
    "https://xpbowler--hackmit-model-generate.modal.run",
    json={
        "prompt": prompt,
    },
    files={"file"}
)

print(response.json().get('answer',None))