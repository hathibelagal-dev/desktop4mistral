import requests
import os


class Client:
    def __init__(self):
        self.base_url = "https://api.mistral.ai/v1/"
        self.api_key = os.environ["MISTRAL_API_KEY"]
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        self.model_data = None
        self.model_id = None

    def _getModels(self):
        if self.model_data is not None:
            return self.model_data

        url = self.base_url + "models"
        response = requests.get(url, headers=self.headers)
        self.model_data = response.json()["data"]
        return self.model_data

    def setModel(self, model_id):
        self.model_id = model_id

    def listModels(self):
        models = self._getModels()
        outputs = []
        for model in models:
            if model["capabilities"]["completion_chat"] and model["id"]:
                outputs.append(model["id"])
        return outputs

    def sendChatMessage(self, messages):
        url = self.base_url + "chat/completions"
        config = {
            "model": self.model_id,
            "messages": messages,
        }
        response = requests.post(url, headers=self.headers, json=config).json()
        return response["choices"][0]["message"]["content"]
