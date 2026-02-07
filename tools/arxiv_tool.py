import arxiv
import requests
import os
import tempfile
import time
from typing import List, Optional, Tuple
import re

def download_pdf_from_url(pdf_url: str, save_dir=None, timeout=30) -> Tuple[Optional[str], Optional[str]]:
    """Download PDF directly from any URL (ArXiv or other)."""
    try:
        if save_dir is None:
            save_dir = tempfile.gettempdir()
        
        filename = pdf_url.split('/')[-1]
        if not filename.endswith('.pdf'):
            arxiv_match = re.search(r'(\d{4}\.\d{4,5})', pdf_url)
            if arxiv_match:
                filename = f"{arxiv_match.group(1)}.pdf"
            else:
                filename = "downloaded_paper.pdf"
        
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = requests.get(pdf_url, timeout=timeout, stream=True)
                response.raise_for_status()
                break
            except requests.RequestException as e:
                if attempt == max_retries - 1:
                    raise
                time.sleep(2 ** attempt)
        
        filepath = os.path.join(save_dir, filename)
        
        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        
        return filepath, None
        
    except requests.Timeout:
        return None, "Download timed out. Check your internet connection."
    except requests.RequestException as e:
        return None, f"Download failed: {str(e)}"
    except OSError as e:
        return None, f"Failed to save file: {str(e)}"
    except Exception as e:
        return None, f"Unexpected error: {str(e)}"

def search_arxiv(query, max_results=5, retry_delay=3) -> Tuple[Optional[List], Optional[str]]:
    """Search ArXiv for papers and return metadata with aggressive rate limit protection."""
    try:
        client = arxiv.Client(
            page_size=3,
            delay_seconds=10.0,
            num_retries=0
        )
        
        search = arxiv.Search(
            query=query,
            max_results=min(max_results, 3),
            sort_by=arxiv.SortCriterion.Relevance
        )
        
        time.sleep(3)
        
        results = list(client.results(search))
        
        if not results:
            return None, "No papers found matching your query. Try different keywords."
        
        return results, None
        
    except arxiv.HTTPError as e:
        error_str = str(e)
        if '429' in error_str or 'Too Many Requests' in error_str:
            return None, (
                "**ArXiv Rate Limit Hit**\n\n"
                "ArXiv's API is very strict about rate limits. Your IP has been temporarily blocked.\n\n"
                "**What happened:**\n"
                "Multiple searches in a short time triggered ArXiv's protection.\n\n"
                "**Solutions:**\n"
                "1. **Wait 10-15 minutes** before trying again\n"
                "2. **Use 'Add PDF by URL'** below instead (bypasses ArXiv search)\n"
                "3. **Upload PDFs directly** from your computer\n"
                "4. Search Google Scholar/ArXiv website, then use method #2\n\n"
                "**Prevention:**\n"
                "- Wait at least 15 seconds between searches\n"
                "- Use specific queries to get results on first try\n\n"
                f"_Error details: {error_str}_"
            )
        else:
            return None, f"ArXiv API error: {error_str}. Please try again later."
    
    except Exception as e:
        return None, f"Search failed: {str(e)}. Please check your internet connection."

def download_pdf(result, save_dir=None, timeout=30) -> Tuple[Optional[str], Optional[str]]:
    """
    Download the PDF of an ArXiv result.
    
    Args:
        result: ArXiv result object
        save_dir: Directory to save PDF (default: temp directory)
        timeout: Download timeout in seconds
    
    Returns:
        Tuple of (filepath, error_message)
        - On success: (filepath, None)
        - On error: (None, error_message)
    """
    try:
        if save_dir is None:
            save_dir = tempfile.gettempdir()
        
        pdf_url = result.pdf_url
        
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = requests.get(pdf_url, timeout=timeout, stream=True)
                response.raise_for_status()
                break
            except requests.RequestException as e:
                if attempt == max_retries - 1:
                    raise
                time.sleep(2 ** attempt)
        
        filename = f"{result.get_short_id()}.pdf"
        filepath = os.path.join(save_dir, filename)
        
        with open(filepath, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        
        return filepath, None
        
    except requests.Timeout:
        return None, "Download timed out. The paper might be too large or network is slow."
    
    except requests.RequestException as e:
        return None, f"Download failed: {str(e)}. Please try again."
    
    except OSError as e:
        return None, f"Failed to save file: {str(e)}. Check disk space and permissions."
    
    except Exception as e:
        return None, f"Unexpected error during download: {str(e)}"