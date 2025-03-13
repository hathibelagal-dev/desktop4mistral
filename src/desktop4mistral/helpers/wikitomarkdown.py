import wikipedia
from markdownify import markdownify

class WikiToMD:
    @staticmethod
    def convert(title):
        try:
            page = wikipedia.page(title)
            
            markdown_content = markdownify(
                page.content,
                heading_style="ATX",
                strong_em_symbol="*",
                strip=['sup', 'script']
            )
            
            markdown_content = '\n\n'.join(line.strip() for line in markdown_content.splitlines() if line.strip())    
            return True, markdown_content
            
        except wikipedia.exceptions.DisambiguationError as e:
            return False, f"Disambiguation error: {e.options}"
        except wikipedia.exceptions.PageError:
            return False, "Page not found"
        
print(WikiToMD.convert("Elon_(name)"))