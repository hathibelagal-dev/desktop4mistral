import requests
import os
from ..commands import Commands
import time
import json
import subprocess

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

    def execute_python_code(self, code):
        with open("temp.py", "w") as f:
            f.write(code)
        process = subprocess.Popen(["python", "temp.py"], stdout=subprocess.PIPE)
        output, _ = process.communicate()
        if not output:
            return "Done."
        return output.decode("utf-8")

    def _handle_tool_call(self, tool_call, messages):
        """Handles a single tool call and updates the messages."""
        function_name = tool_call["function"]["name"]
        arguments = json.loads(tool_call["function"]["arguments"])
        tool_call_id = tool_call["id"]

        if function_name == "execute_python_code":
            result = self.execute_python_code(arguments["code"])
        elif function_name == "read_local_file":
            try:
                with open(arguments["file"], "r") as f:
                    result = f.read()
            except FileNotFoundError:
                result = "I couldn't find that file."
            except PermissionError:
                result = "I don't have permission to read that file."
            except Exception as e:
                result = f"An unexpected error occurred: {e}"
        elif function_name == "write_local_file":
            try:
                with open(arguments["file"], "w") as f:
                    f.write(arguments["text"])
                    result = "Done."
            except PermissionError:
                result = "I don't have permission to write to that file."
            except Exception as e:
                result = f"An unexpected error occurred: {e}"
        else:
            result = f"Unknown tool function: {function_name}"

        time.sleep(3)  # Add a delay after tool execution
        tool_message = {
            "role": "tool",
            "name": function_name,
            "content": result,
            "tool_call_id": tool_call_id,
        }
        messages.append(tool_message)
        return result

    def sendChatMessage(self, messages):
        print(messages)
        url = self.base_url + "chat/completions"
        config = {
            "model": self.model_id,
            "messages": messages,
            "tools": Commands.get_tools(),
            "parallel_tool_calls": False
        }
        response = requests.post(url, headers=self.headers, json=config).json()
        print(response)

        if response["choices"][0]["message"]["tool_calls"]:
            tool_call = response["choices"][0]["message"]["tool_calls"][0]
            messages.append(response["choices"][0]["message"])
            return self._handle_tool_call(tool_call, messages)
        else:
            return response["choices"][0]["message"]["content"]
