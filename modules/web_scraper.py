import requests
from bs4 import BeautifulSoup
from typing import Dict
import config
from urllib.parse import urlparse

class WebScraper:
    """استخراج کننده اطلاعات وبسایت"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': config.USER_AGENT})
    
    def scrape_website(self, url: str) -> Dict:
        """
        استخراج اطلاعات از وبسایت
        
        Args:
            url: آدرس وبسایت
            
        Returns:
            دیکشنری حاوی اطلاعات وبسایت
        """
        try:
            response = self.session.get(url, timeout=config.REQUEST_TIMEOUT)
            response.encoding = 'utf-8'
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            return {
                'url': url,
                'title': soup.title.string if soup.title else 'نامشخص',
                'html_content': str(soup),
                'text_content': soup.get_text(),
            }
        
        except Exception as e:
            print(f"خطا در بارگذاری {url}: {str(e)}")
            return None
    
    def get_domain_name(self, url: str) -> str:
        """
        استخراج نام دامنه از URL
        
        Args:
            url: آدرس وب
            
        Returns:
            نام دامنه
        """
        parsed = urlparse(url)
        domain = parsed.netloc.replace('www.', '')
        return domain