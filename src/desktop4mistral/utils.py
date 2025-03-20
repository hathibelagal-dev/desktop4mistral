from pathlib import Path
import os
import json
from datetime import datetime

class Utils:
    @staticmethod    
    def get_home_path():
        return Path.home()

    @staticmethod
    def get_documents_path():
        return os.path.join(Utils.get_home_path(), "Documents")

    @staticmethod
    def generate_filename(extension="txt"):
        current_time = datetime.now()        
        timestamp = current_time.strftime("%Y%m%d_%H%M%S")
        return os.path.join(
            Utils.get_documents_path(),
            f"conversation_{timestamp}.{extension}"
        )

    @staticmethod
    def to_json(messages):
        contents = json.dumps(messages)
        filename = Utils.generate_filename("json")
        with open(filename, "w") as file:
            file.write(contents)
        return filename
    
    @staticmethod
    def to_markdown(messages):
        filename = Utils.generate_filename("md")
        with open(filename, "w") as file:
            for message in messages:
                if message["role"] == "system":
                    continue
                file.write("#### " + message["role"] + "\n\n")
                file.write(message["content"] + "\n\n")
                file.write("---\n\n")
        return filename

