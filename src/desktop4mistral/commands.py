import requests

class Commands:
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

        return False