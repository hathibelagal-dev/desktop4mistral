import markdown


class MarkdownConverter:
    def __init__(self):
        self.markdown = markdown.Markdown(extensions=["tables", "fenced_code"])

    def convert(self, text):
        return self.markdown.convert(text)
