import re
from typing import List, Dict, Set
import config
from urllib.parse import urlparse

class ContactExtractor:
    """استخراج کننده اطلاعات تماس"""
    
    def __init__(self):
        self.email_pattern = config.EMAIL_PATTERN
        self.phone_patterns = config.PHONE_PATTERNS
    
    def extract_emails(self, text: str) -> Set[str]:
        """
        استخراج ایمیل ها از متن
        
        Args:
            text: متن مورد بررسی
            
        Returns:
            مجموعه ایمیل های یافت شده
        """
        emails = set(re.findall(self.email_pattern, text))
        return emails
    
    def extract_phones(self, text: str) -> Set[str]:
        """
        استخراج شماره های تماس از متن
        
        Args:
            text: متن مورد بررسی
            
        Returns:
            مجموعه شماره های تماس یافت شده
        """
        phones = set()
        for pattern in self.phone_patterns:
            try:
                found = re.findall(pattern, text)
                phones.update(found)
            except:
                pass
        return phones
    
    def extract_contact_info(self, website_data: Dict) -> Dict:
        """
        استخراج تمام اطلاعات تماس
        
        Args:
            website_data: داده های وبسایت
            
        Returns:
            دیکشنری حاوی اطلاعات تماس
        """
        if not website_data:
            return None
            
        text_content = website_data.get('text_content', '')
        html_content = website_data.get('html_content', '')
        combined_text = text_content + html_content
        
        return {
            'emails': list(self.extract_emails(combined_text)),
            'phones': list(self.extract_phones(combined_text)),
            'website_name': website_data.get('title'),
            'website_url': website_data.get('url'),
            'domain': self.extract_domain(website_data.get('url', '')),
        }
    
    def extract_domain(self, url: str) -> str:
        """
        استخراج دامنه از URL
        
        Args:
            url: آدرس وب
            
        Returns:
            نام دامنه
        """
        try:
            parsed = urlparse(url)
            return parsed.netloc.replace('www.', '')
        except:
            return ''