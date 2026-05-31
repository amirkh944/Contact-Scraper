import requests
from typing import List, Dict
import config

class GoogleSearchEngine:
    """موتور جستجو Google Custom Search Engine"""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or config.GOOGLE_CSE_API_KEY
        self.cse_id = config.GOOGLE_CSE_ID
        self.base_url = "https://www.googleapis.com/customsearch/v1"
    
    def search(self, keywords: str, num_results: int = 20) -> List[Dict]:
        """
        جستجو در گوگل با استفاده از Custom Search Engine
        
        Args:
            keywords: کلمات کلیدی برای جستجو
            num_results: تعداد نتایج مورد نظر
            
        Returns:
            لیست نتایج جستجو
        """
        try:
            params = {
                'q': keywords,
                'cx': self.cse_id,
                'key': self.api_key,
                'num': min(num_results, 10),
                'start': 1
            }
            
            response = requests.get(self.base_url, params=params, timeout=config.REQUEST_TIMEOUT)
            response.raise_for_status()
            
            results = response.json().get('items', [])
            search_results = []
            
            for item in results:
                search_results.append({
                    'title': item.get('title'),
                    'link': item.get('link'),
                    'snippet': item.get('snippet'),
                })
            
            return search_results
        
        except Exception as e:
            print(f"خطا در جستجو: {str(e)}")
            return []