import urllib.request
import urllib.parse
import re
import json

def execute_search(query_string):
    """Queries the web structure cleanly, returning summarized content snippets."""
    url = "https://lite.duckduckgo.com/lite/"
    data = urllib.parse.urlencode({"q": query_string}).encode("utf-8")
    try:
        req = urllib.request.Request(url, data=data, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10) as response:
            html = response.read().decode('utf-8')
            
        snippets = re.findall(r'<td class="result-snippet">(.*?)</td>', html, re.DOTALL)[:3]
        clean_snippets = [re.sub(r'<.*?>', '', s).strip() for s in snippets]
        
        if not clean_snippets:
            return {"status": "success", "results": ["No immediate text snippets returned."]}
        return {"status": "success", "results": clean_snippets}
    except Exception as e:
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
        print(json.dumps(execute_search(query)))
