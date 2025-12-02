import requests
import json
import os
import time
import re

def escape_latex(text):
    """Escapes special LaTeX characters."""
    if not isinstance(text, str):
        return str(text)
    chars = {
        '&': r'\&',
        '%': r'\%',
        '$': r'\$',
        '#': r'\#',
        '_': r'\_',
        '{': r'\{',
        '}': r'\}',
        '~': r'\textasciitilde{}',
        '^': r'\^{}',
        '\\': r'\textbackslash{}',
        '<': r'\textless{}',
        '>': r'\textgreater{}',
    }
    return ''.join(chars.get(c, c) for c in text)

def convert_html_to_latex(text):
    """Converts HTML tags to LaTeX and escapes special characters."""
    if not isinstance(text, str):
        return str(text)
    
    # First, handle italics with padding to prevent merging
    text = re.sub(r'<i>(.*?)</i>', r' \\textit{\1} ', text)
    text = re.sub(r'<em>(.*?)</em>', r' \\textit{\1} ', text)
    
    # Remove other tags
    text = re.sub(r'<[^>]+>', '', text)
    
    # Collapse multiple spaces
    text = re.sub(r'\s+', ' ', text).strip()
    
    # Fix punctuation spacing (remove space before . , ; :)
    text = re.sub(r'\s+([.,;:])', r'\1', text)
    
    # Escape special characters (but preserve \textit{...})
    parts = re.split(r'(\\textit\{.*?\})', text)
    escaped_parts = []
    for part in parts:
        if part.startswith(r'\textit{'):
            # Extract content inside \textit{}
            content = part[8:-1]
            # Escape content inside italics
            escaped_content = escape_latex(content)
            escaped_parts.append(r'\textit{' + escaped_content + '}')
        else:
            escaped_parts.append(escape_latex(part))
            
    return ''.join(escaped_parts)

def fetch_citation(doi):
    """Fetch citation data from CrossRef API."""
    url = f"https://api.crossref.org/works/{doi}"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
        item = data['message']
        
        # Extract fields
        title = item.get('title', [''])[0]
        container_title = item.get('container-title', [''])[0] # Journal
        published = item.get('published-print', item.get('published-online', {}))
        year = published.get('date-parts', [[None]])[0][0]
        
        # Clean and Escape
        title = convert_html_to_latex(title)
        container_title = convert_html_to_latex(container_title)
        
        authors = []
        if 'author' in item:
            for author in item['author']:
                family = author.get('family', '')
                given = author.get('given', '')
                if family:
                    # Escape author names too
                    family = escape_latex(family)
                    given = escape_latex(given)
                    authors.append(f"{family} {given[0] if given else ''}.")
        
        if len(authors) > 2:
            author_str = f"{authors[0]} et al."
        elif len(authors) == 2:
            author_str = f"{authors[0]} and {authors[1]}"
        elif len(authors) == 1:
            author_str = authors[0]
        else:
            author_str = "Unknown"

        # Format: Author (Year). Title. Journal. DOI
        citation = f"{author_str} ({year}). {title}. \\textit{{{container_title}}}. DOI: \\href{{https://doi.org/{doi}}}{{{doi}}}"
        return citation
        
    except Exception as e:
        print(f"Error fetching {doi}: {e}")
        return f"DOI: \\href{{https://doi.org/{doi}}}{{{doi}}}"

def get_bibliography(config_path="config_dois.json", cache_path="bibliography_cache.json"):
    """Load DOIs from config and fetch citations."""
    with open(config_path, "r") as f:
        doi_config = json.load(f)
        
    if os.path.exists(cache_path):
        with open(cache_path, "r") as f:
            cache = json.load(f)
    else:
        cache = {}
        
    results = {}
    
    for gene, dois in doi_config.items():
        results[gene] = []
        for doi in dois:
            if doi in cache:
                results[gene].append(cache[doi])
            else:
                print(f"Fetching {doi}...")
                citation = fetch_citation(doi)
                cache[doi] = citation
                results[gene].append(citation)
                time.sleep(0.5) # Be nice to API
                
    with open(cache_path, "w") as f:
        json.dump(cache, f, indent=4)
        
    return results

if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    config_path = os.path.join(base_dir, "config", "config_dois.json")
    cache_path = os.path.join(base_dir, "cache", "bibliography_cache.json")
    
    bib = get_bibliography(config_path, cache_path)
    print(f"Loaded {len(bib)} genes from bibliography.")
