import requests
from bs4 import BeautifulSoup
from typing import List, Dict
from urllib.parse import quote
import config
import time

class GoogleSearchEngine:
    """موتور جستجو Google Custom Search Engine"""
    
    def __init__(self, cse_id: str = None):
        self.cse_id = cse_id or config.GOOGLE_CSE_ID
        self.base_url = f"https://cse.google.com/cse"
        self.session = requests.Session()
        self.session.headers.update({'User-Agent': config.USER_AGENT})
    
    def search(self, keywords: str, num_results: int = 20) -> List[Dict]:
        """
        جستجو در Google Custom Search Engine با اسکرپ کردن نتایج
        
        Args:
            keywords: کلمات کلیدی برای جستجو
            num_results: تعداد نتایج مورد نظر
            
        Returns:
            لیست نتایج جستجو
        """
        try:
            search_results = []
            
            # محاسبه تعداد صفحات مورد نیاز
            results_per_page = 10
            num_pages = (num_results + results_per_page - 1) // results_per_page
            
            for page in range(num_pages):
                # ساخت URL جستجو
                start = page * results_per_page + 1
                search_url = self._build_search_url(keywords, start)
                
                print(f"درحال جستجو صفحه {page + 1}: {search_url}")
                
                # دریافت صفحه جستجو
                try:
                    response = self.session.get(search_url, timeout=config.REQUEST_TIMEOUT)
                    response.encoding = 'utf-8'
                    response.raise_for_status()
                except Exception as e:
                    print(f"خطا در دریافت صفحه: {str(e)}")
                    continue
                
                # استخراج نتایج از HTML
                page_results = self._parse_search_results(response.text)
                
                if not page_results:
                    print(f"هیچ نتیجه‌ای در صفحه {page + 1} یافت نشد")
                    break
                
                search_results.extend(page_results)
                
                # توقف اگر به تعداد مورد نظر رسیدیم
                if len(search_results) >= num_results:
                    search_results = search_results[:num_results]
                    break
                
                # تاخیر برای جلوگیری از مسدود شدن
                if page < num_pages - 1:
                    time.sleep(2)
            
            return search_results
        
        except Exception as e:
            print(f"خطا در جستجو: {str(e)}")
            return []
    
    def _build_search_url(self, keywords: str, start: int = 1) -> str:
        """
        ساخت URL جستجو برای Google Custom Search
        
        Args:
            keywords: کلمات کلیدی
            start: شماره شروع نتایج
            
        Returns:
            URL جستجو
        """
        params = {
            'cx': self.cse_id,
            'q': keywords,
            'num': 10,
            'start': start,
            'sort': ''
        }
        
        # ساخت string پارامترها
        param_str = '&'.join([f'{key}={quote(str(value))}' for key, value in params.items()])
        return f"{self.base_url}?{param_str}"
    
    def _parse_search_results(self, html_content: str) -> List[Dict]:
        """
        استخراج نتایج جستجو از HTML
        
        Args:
            html_content: محتوای HTML صفحه جستجو
            
        Returns:
            لیست نتایج استخراج شده
        """
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            results = []
            
            # البحث عن عناصر نتائج البحث
            # Google CSE عادة يستخدم divs مع فئات معينة للنتائج
            
            # محاولة 1: البحث عن div.gsc-webResult
            result_divs = soup.find_all('div', class_='gsc-webResult')
            
            if not result_divs:
                # محاولة 2: البحث عن عناصر مع class gsc-result
                result_divs = soup.find_all('div', class_='gsc-result')
            
            if not result_divs:
                # محاولة 3: البحث عن عناصر a مع class gsc-title
                links = soup.find_all('a', class_='gsc-title')
                for link in links:
                    url = link.get('href', '')
                    if url:
                        result = {
                            'title': link.get_text(strip=True),
                            'link': url,
                            'snippet': ''
                        }
                        results.append(result)
                return results
            
            # استخراج نتایج
            for result_div in result_divs:
                try:
                    # استخراج عنوان و لینک
                    title_link = result_div.find('a', class_='gsc-title')
                    if not title_link:
                        title_link = result_div.find('a')
                    
                    if not title_link:
                        continue
                    
                    url = title_link.get('href', '')
                    title = title_link.get_text(strip=True)
                    
                    if not url or not title:
                        continue
                    
                    # استخراج snippet
                    snippet_div = result_div.find('div', class_='gsc-snippet')
                    snippet = ''
                    if snippet_div:
                        snippet = snippet_div.get_text(strip=True)
                    
                    result = {
                        'title': title,
                        'link': url,
                        'snippet': snippet
                    }
                    results.append(result)
                
                except Exception as e:
                    print(f"خطا در استخراج نتیجه: {str(e)}")
                    continue
            
            return results
        
        except Exception as e:
            print(f"خطا در تجزیه HTML: {str(e)}")
            return []
    
    def get_domain_name(self, url: str) -> str:
        """
        استخراج نام دامنه از URL
        
        Args:
            url: آدرس وب
            
        Returns:
            نام دامنه
        """
        from urllib.parse import urlparse
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.replace('www.', '')
            return domain
        except:
            return ''
