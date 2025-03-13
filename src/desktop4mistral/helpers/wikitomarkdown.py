import wikipedia
from markdownify import markdownify
import requests

class WikiHelper:
    @staticmethod
    def convert_to_md(pageid):
        try:
            page = wikipedia.page(pageid=pageid)
            print(page)
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
        
    @staticmethod
    def search(query):
        url = "https://en.wikipedia.org/w/api.php"
        params = {
            "action": "query",
            "format": "json",
            "list": "search",
            "srsearch": query
        }
        response = requests.get(url, params=params)
        data = response.json()
        search_results = data["query"]["search"]
        search_results = [{'title': result['title'], 'pageid': result['pageid']} for result in search_results]
        return search_results
        
    
