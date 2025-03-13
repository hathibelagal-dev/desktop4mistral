import requests
from .helpers.wikitomarkdown import WikiHelper

class Commands:
    def system_prompt(self):
        return """You can run python and javascript by saying /py
        or /js followed by the code you want to run enclosed in a
        pair of << and >>. You should prefer using this feature
        instead of working out the calculation yourself. Note, this
        is just for running the code. Don't use this syntax unnecessarily,
        like when you just want to tell the user how to do something. And when
        you use this syntax, don't say anything else in that message.

        To read a file in the local filesystem, just say /read followed
        by the absolute path of file. Don't say anything else in that
        message.
        """

    def handle_command(self, messages):
        message = messages[-1]["content"]
        command = message.strip().split(" ")[0]
        if not command.startswith("/"):
            return False
        if command == "/read":
            to_read = message[len(command):].strip()
            if to_read.startswith("http://") or to_read.startswith("https://"):
                print("Now reading remote file:" + to_read)
                remote_file_contents = requests.get(to_read).text
                remote_file_contents = f"""The contents of {to_read} are:\n\n```\n{remote_file_contents}```"""
                return remote_file_contents
            print("Now reading local file:" + to_read)
            try:
                with open(to_read, "r") as f:
                    contents = f.read()
                    contents = f"""The contents of {to_read} are:\n\n```\n{contents}```"""                
                    return contents
            except FileNotFoundError:
                return "I couldn't find that file."
            except PermissionError:
                return "I don't have permission to read that file."
            except Exception as e:
                return f"An unexpected error occurred: {e}"            
        elif command == "/wiki_id":
            to_read = message[len(command):].strip()
            print("Now reading wiki:" + to_read)
            success, contents = WikiHelper.convert_to_md(to_read)
            if success:
                return f"""The contents of that wiki page are ```\n{contents}\n```"""
            else:
                return "I couldn't read that wiki page."
        elif command == "/wiki_search":
            to_read = message[len(command):].strip()
            print("Now searching wiki:" + to_read)
            results = WikiHelper.search(to_read)
            contents = "```\n"
            for result in results:
                contents += f"{result['pageid']} --> {result['title']}\n\n"
            contents += "```"
            return contents

        return False