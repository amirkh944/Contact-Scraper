"""
تنظیمات اپلیکیشن
"""

# Google Custom Search Engine Settings
GOOGLE_CSE_ID = "51fde782e13b723e3"  # شناسه Custom Search Engine خود را جایگزین کنید
GOOGLE_CSE_API_KEY = ""  # API Key خود را جایگزین کنید

# Web Scraping Settings
REQUEST_TIMEOUT = 10
MAX_PAGES_PER_SEARCH = 2
MAX_SITES_TO_SCRAPE = 20

# Regex Patterns for Contact Information
EMAIL_PATTERN = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
PHONE_PATTERNS = [
    r'\+?98[0-9]{9,}',  # Iranian numbers with +98
    r'0[0-9]{10}',       # Iranian numbers starting with 0
    r'\+?[0-9]{1,3}[0-9]{8,}',  # International format
    r'[0-9]{3}[-.]?[0-9]{3}[-.]?[0-9]{4}',  # Standard format
]

# Export Settings
EXPORT_FORMATS = ['Excel', 'CSV', 'JSON']

# UI Settings
APP_TITLE = "استخراج کننده اطلاعات تماس"
APP_STYLE = "Fusion"

# Browser Settings
HEADLESS_MODE = True
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"

# Logging
LOG_LEVEL = "INFO"
LOG_FILE = "app.log"