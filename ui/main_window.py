from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QTableWidget,
    QTableWidgetItem, QProgressBar, QTabWidget,
    QGroupBox, QSpinBox, QCheckBox, QComboBox,
    QMessageBox, QFileDialog, QStatusBar, QApplication
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QIcon, QFont
import sys
import os
import traceback

from modules.google_search import GoogleSearchEngine
from modules.web_scraper import WebScraper
from modules.contact_extractor import ContactExtractor
from modules.data_manager import DataManager
from ui.styles import STYLESHEET
from ui.dialogs import show_error, show_info, show_warning
import config

class ScraperWorker(QThread):
    """Worker thread برای جستجو و استخراج"""
    progress = pyqtSignal(str)
    finished = pyqtSignal(list)
    error = pyqtSignal(str)
    
    def __init__(self, keywords: str, max_results: int, api_key: str, cse_id: str):
        super().__init__()
        self.keywords = keywords
        self.max_results = max_results
        self.api_key = api_key
        self.cse_id = cse_id
        self.results = []
    
    def run(self):
        try:
            self.progress.emit("شروع جستجو...")
            
            search_engine = GoogleSearchEngine(self.api_key)
            search_engine.cse_id = self.cse_id
            search_results = search_engine.search(self.keywords, self.max_results)
            
            if not search_results:
                self.error.emit("نتایج جستجو یافت نشد. لطفا API Key و CSE ID را بررسی کنید.")
                return
            
            scraper = WebScraper()
            extractor = ContactExtractor()
            
            for i, search_result in enumerate(search_results[:self.max_results]):
                self.progress.emit(f"در حال پردازش ({i+1}/{len(search_results)}): {search_result['title'][:50]}...")
                
                website_data = scraper.scrape_website(search_result['link'])
                if website_data:
                    contact_info = extractor.extract_contact_info(website_data)
                    if contact_info and (contact_info.get('emails') or contact_info.get('phones')):
                        self.results.append(contact_info)
            
            self.progress.emit("تکمیل جستجو...")
            self.finished.emit(self.results)
        
        except Exception as e:
            self.error.emit(f"خطا: {str(e)}\n{traceback.format_exc()}")

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(config.APP_TITLE)
        self.setGeometry(100, 100, 1400, 900)
        self.setStyleSheet(STYLESHEET)
        
        # RTL Support
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        
        self.data_manager = DataManager()
        self.results = []
        self.worker = None
        
        self.init_ui()
    
    def init_ui(self):
        """ایجاد رابط کاربری"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(10)
        
        # Tab Widget
        self.tabs = QTabWidget()
        
        # Tab 1: Search
        search_tab = self.create_search_tab()
        self.tabs.addTab(search_tab, "🔍 جستجو")
        
        # Tab 2: Results
        results_tab = self.create_results_tab()
        self.tabs.addTab(results_tab, "📊 نتایج")
        
        # Tab 3: Settings
        settings_tab = self.create_settings_tab()
        self.tabs.addTab(settings_tab, "⚙️ تنظیمات")
        
        main_layout.addWidget(self.tabs)
        
        # Status Bar
        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)
        self.statusbar.showMessage("آماده برای جستجو")
        
        central_widget.setLayout(main_layout)
    
    def create_search_tab(self) -> QWidget:
        """تب جستجو"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Keywords input
        keywords_group = QGroupBox("کلمات کلیدی و تنظیمات جستجو")
        keywords_layout = QVBoxLayout()
        
        label = QLabel("کلمات کلیدی (مثال: خدمات نقل و انتقالات):")
        self.keywords_input = QLineEdit()
        self.keywords_input.setPlaceholderText("کلمات کلیدی را وارد کنید...")
        self.keywords_input.setMinimumHeight(35)
        keywords_layout.addWidget(label)
        keywords_layout.addWidget(self.keywords_input)
        
        # Options
        options_layout = QHBoxLayout()
        
        label = QLabel("تعداد نتایج:")
        self.max_results_spinbox = QSpinBox()
        self.max_results_spinbox.setMinimum(1)
        self.max_results_spinbox.setMaximum(100)
        self.max_results_spinbox.setValue(10)
        self.max_results_spinbox.setMinimumWidth(80)
        
        options_layout.addWidget(label)
        options_layout.addWidget(self.max_results_spinbox)
        
        label2 = QLabel("حد زمانی (ثانیه):")
        self.timeout_spinbox = QSpinBox()
        self.timeout_spinbox.setValue(config.REQUEST_TIMEOUT)
        self.timeout_spinbox.setMinimumWidth(80)
        
        options_layout.addWidget(label2)
        options_layout.addWidget(self.timeout_spinbox)
        options_layout.addStretch()
        
        keywords_layout.addLayout(options_layout)
        keywords_group.setLayout(keywords_layout)
        layout.addWidget(keywords_group)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setMinimumHeight(25)
        layout.addWidget(self.progress_bar)
        
        # Progress label
        self.progress_label = QLabel("")
        self.progress_label.setStyleSheet("color: #27ae60; font-weight: bold;")
        layout.addWidget(self.progress_label)
        
        # Buttons
        buttons_layout = QHBoxLayout()
        
        self.search_button = QPushButton("🚀 شروع جستجو")
        self.search_button.setMinimumHeight(40)
        self.search_button.setFont(QFont('Arial', 11, QFont.Weight.Bold))
        self.search_button.clicked.connect(self.start_search)
        buttons_layout.addWidget(self.search_button)
        
        stop_button = QPushButton("⏹️ متوقف کردن")
        stop_button.setMinimumHeight(40)
        stop_button.clicked.connect(self.stop_search)
        buttons_layout.addWidget(stop_button)
        
        clear_button = QPushButton("🗑️ پاک کردن")
        clear_button.setMinimumHeight(40)
        clear_button.clicked.connect(self.clear_input)
        buttons_layout.addWidget(clear_button)
        
        layout.addLayout(buttons_layout)
        layout.addStretch()
        
        widget.setLayout(layout)
        return widget
    
    def create_results_tab(self) -> QWidget:
        """تب نتایج"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Info label
        info_label = QLabel("")
        self.info_label = info_label
        layout.addWidget(info_label)
        
        # Results table
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(5)
        self.results_table.setHorizontalHeaderLabels(
            ['وبسایت', 'دامنه', 'لینک', 'ایمیل', 'تماس']
        )
        self.results_table.setColumnWidth(0, 180)
        self.results_table.setColumnWidth(1, 150)
        self.results_table.setColumnWidth(2, 250)
        self.results_table.setColumnWidth(3, 200)
        self.results_table.setColumnWidth(4, 200)
        self.results_table.setMinimumHeight(400)
        
        # Right-click context menu
        self.results_table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.results_table.customContextMenuRequested.connect(self.show_table_context_menu)
        
        layout.addWidget(self.results_table)
        
        # Export buttons
        export_layout = QHBoxLayout()
        
        excel_button = QPushButton("📊 صادر به Excel")
        excel_button.setMinimumHeight(35)
        excel_button.clicked.connect(lambda: self.export_data('excel'))
        export_layout.addWidget(excel_button)
        
        csv_button = QPushButton("📄 صادر به CSV")
        csv_button.setMinimumHeight(35)
        csv_button.clicked.connect(lambda: self.export_data('csv'))
        export_layout.addWidget(csv_button)
        
        json_button = QPushButton("📋 صادر به JSON")
        json_button.setMinimumHeight(35)
        json_button.clicked.connect(lambda: self.export_data('json'))
        export_layout.addWidget(json_button)
        
        copy_button = QPushButton("📋 کپی به کلیپ بورد")
        copy_button.setMinimumHeight(35)
        copy_button.clicked.connect(self.copy_to_clipboard)
        export_layout.addWidget(copy_button)
        
        export_layout.addStretch()
        
        layout.addLayout(export_layout)
        
        widget.setLayout(layout)
        return widget
    
    def create_settings_tab(self) -> QWidget:
        """تب تنظیمات"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # API Settings
        api_group = QGroupBox("تنظیمات Google Custom Search Engine")
        api_layout = QVBoxLayout()
        
        cse_label = QLabel("شناسه Custom Search Engine (CSE ID):")
        self.cse_id_input = QLineEdit()
        self.cse_id_input.setText(config.GOOGLE_CSE_ID)
        self.cse_id_input.setMinimumHeight(35)
        api_layout.addWidget(cse_label)
        api_layout.addWidget(self.cse_id_input)
        
        api_key_label = QLabel("API Key (کلید API):")
        self.api_key_input = QLineEdit()
        self.api_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.api_key_input.setText(config.GOOGLE_CSE_API_KEY)
        self.api_key_input.setMinimumHeight(35)
        api_layout.addWidget(api_key_label)
        api_layout.addWidget(self.api_key_input)
        
        show_api_key_checkbox = QCheckBox("نمایش API Key")
        show_api_key_checkbox.stateChanged.connect(self.toggle_api_key_visibility)
        api_layout.addWidget(show_api_key_checkbox)
        
        api_group.setLayout(api_layout)
        layout.addWidget(api_group)
        
        # Scraping Settings
        scrape_group = QGroupBox("تنظیمات جمع آوری داده ها")
        scrape_layout = QVBoxLayout()
        
        timeout_label = QLabel("حد زمانی درخواست (ثانیه):")
        self.settings_timeout_spinbox = QSpinBox()
        self.settings_timeout_spinbox.setValue(config.REQUEST_TIMEOUT)
        self.settings_timeout_spinbox.setMinimum(5)
        self.settings_timeout_spinbox.setMaximum(60)
        scrape_layout.addWidget(timeout_label)
        scrape_layout.addWidget(self.settings_timeout_spinbox)
        
        scrape_group.setLayout(scrape_layout)
        layout.addWidget(scrape_group)
        
        # Information
        info_group = QGroupBox("اطلاعات")
        info_layout = QVBoxLayout()
        
        info_text = QLabel(
            "<b>راهنمای استفاده:</b><br>"
            "1. شناسه Custom Search Engine خود را وارد کنید<br>"
            "2. API Key Google Custom Search را تنظیم کنید<br>"
            "3. کلمات کلیدی را در تب جستجو وارد کنید<br>"
            "4. بر روی 'شروع جستجو' کلیک کنید<br>"
            "5. نتایج را مشاهده و صادر کنید<br><br>"
            "<b>نکات مهم:</b><br>"
            "• حد زمانی پیش فرض 10 ثانیه است<br>"
            "• برای دریافت API Key به <a href='https://console.cloud.google.com'>Google Cloud Console</a> مراجعه کنید<br>"
            "• نتایج صادر شده در پوشه 'data/results' ذخیره می‌شوند"
        )
        info_text.setOpenExternalLinks(True)
        info_layout.addWidget(info_text)
        
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)
        
        # Save button
        save_button = QPushButton("💾 ذخیره تنظیمات")
        save_button.setMinimumHeight(40)
        save_button.clicked.connect(self.save_settings)
        layout.addWidget(save_button)
        
        layout.addStretch()
        
        widget.setLayout(layout)
        return widget
    
    def toggle_api_key_visibility(self, state):
        """نمایش یا پنهان کردن API Key"""
        if state:
            self.api_key_input.setEchoMode(QLineEdit.EchoMode.Normal)
        else:
            self.api_key_input.setEchoMode(QLineEdit.EchoMode.Password)
    
    def start_search(self):
        """شروع جستجو"""
        keywords = self.keywords_input.text().strip()
        
        if not keywords:
            show_warning(self, "هشدار", "لطفاً کلمات کلیدی را وارد کنید")
            return
        
        api_key = self.api_key_input.text().strip()
        cse_id = self.cse_id_input.text().strip()
        
        if not api_key:
            show_warning(self, "هشدار", "لطفاً API Key را وارد کنید")
            return
        
        if not cse_id:
            show_warning(self, "هشدار", "لطفاً Custom Search Engine ID را وارد کنید")
            return
        
        self.search_button.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.progress_label.setText("در حال جستجو...")
        self.statusbar.showMessage("جستجو در حال انجام...")
        
        max_results = self.max_results_spinbox.value()
        self.worker = ScraperWorker(keywords, max_results, api_key, cse_id)
        self.worker.progress.connect(self.update_progress)
        self.worker.finished.connect(self.on_search_finished)
        self.worker.error.connect(self.on_search_error)
        self.worker.start()
    
    def stop_search(self):
        """متوقف کردن جستجو"""
        if self.worker and self.worker.isRunning():
            self.worker.terminate()
            self.worker.wait()
            self.search_button.setEnabled(True)
            self.progress_bar.setVisible(False)
            self.statusbar.showMessage("جستجو متوقف شد")
            show_info(self, "متوقف شد", "جستجو با موفقیت متوقف شد")
    
    def update_progress(self, message: str):
        """بروزرسانی پیشرفت"""
        self.progress_label.setText(message)
        self.progress_bar.setValue((self.progress_bar.value() + 5) % 100)
    
    def on_search_finished(self, results: list):
        """جستجو تمام شد"""
        self.results = results
        self.display_results(results)
        
        self.search_button.setEnabled(True)
        self.progress_bar.setVisible(False)
        self.progress_label.setText(f"✓ جستجو تکمیل شد - {len(results)} نتیجه یافت شد")
        self.progress_label.setStyleSheet("color: #27ae60; font-weight: bold;")
        self.statusbar.showMessage(f"جستجو تکمیل شد - {len(results)} نتیجه")
        self.info_label.setText(f"تعداد نتایج: {len(results)}")
    
    def on_search_error(self, error: str):
        """خطا در جستجو"""
        show_error(self, "خطا", error)
        self.search_button.setEnabled(True)
        self.progress_bar.setVisible(False)
        self.progress_label.setText("❌ خطا در جستجو")
        self.progress_label.setStyleSheet("color: #e74c3c; font-weight: bold;")
        self.statusbar.showMessage("خطا در جستجو")
    
    def display_results(self, results: list):
        """نمایش نتایج"""
        self.results_table.setRowCount(0)
        
        for i, result in enumerate(results):
            self.results_table.insertRow(i)
            
            items = [
                result.get('website_name', ''),
                result.get('domain', ''),
                result.get('website_url', ''),
                ', '.join(result.get('emails', [])),
                ', '.join(result.get('phones', [])),
            ]
            
            for j, item in enumerate(items):
                table_item = QTableWidgetItem(str(item))
                table_item.setToolTip(str(item))
                self.results_table.setItem(i, j, table_item)
    
    def export_data(self, format_type: str):
        """صادر کردن داده ها"""
        if not self.results:
            show_warning(self, "هشدار", "هیچ داده ای برای صادر کردن وجود ندارد")
            return
        
        try:
            if format_type == 'excel':
                filepath = self.data_manager.export_to_excel(self.results)
                format_name = 'Excel'
            elif format_type == 'csv':
                filepath = self.data_manager.export_to_csv(self.results)
                format_name = 'CSV'
            elif format_type == 'json':
                filepath = self.data_manager.export_to_json(self.results)
                format_name = 'JSON'
            
            show_info(
                self, "موفقیت",
                f"داده ها با موفقیت به {format_name} صادر شدند:\n{filepath}"
            )
            
            # Open folder
            os.startfile(os.path.dirname(filepath))
        
        except Exception as e:
            show_error(self, "خطا", f"خطا در صادر کردن: {str(e)}")
    
    def copy_to_clipboard(self):
        """کپی نتایج به کلیپ بورد"""
        if not self.results:
            show_warning(self, "هشدار", "هیچ داده ای برای کپی کردن وجود ندارد")
            return
        
        try:
            clipboard_text = ""
            for result in self.results:
                clipboard_text += f"وبسایت: {result.get('website_name', '')}\n"
                clipboard_text += f"دامنه: {result.get('domain', '')}\n"
                clipboard_text += f"لینک: {result.get('website_url', '')}\n"
                clipboard_text += f"ایمیل: {', '.join(result.get('emails', []))}\n"
                clipboard_text += f"تماس: {', '.join(result.get('phones', []))}\n"
                clipboard_text += "-" * 60 + "\n"
            
            from PyQt6.QtWidgets import QApplication
            QApplication.clipboard().setText(clipboard_text)
            show_info(self, "موفقیت", "نتایج با موفقیت به کلیپ بورد کپی شدند")
        
        except Exception as e:
            show_error(self, "خطا", f"خطا در کپی کردن: {str(e)}")
    
    def show_table_context_menu(self, position):
        """نمایش منوی راست کلیک روی جدول"""
        from PyQt6.QtWidgets import QMenu
        
        menu = QMenu()
        menu.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        
        copy_action = menu.addAction("کپی")
        delete_action = menu.addAction("حذف سطر")
        
        action = menu.exec(self.results_table.mapToGlobal(position))
        
        if action == delete_action:
            row = self.results_table.rowAt(position.y())
            if row >= 0:
                self.results_table.removeRow(row)
                del self.results[row]
    
    def clear_input(self):
        """پاک کردن ورودی ها"""
        self.keywords_input.clear()
        self.results_table.setRowCount(0)
        self.results = []
        self.progress_label.setText("")
        self.info_label.setText("")
        self.statusbar.showMessage("آماده برای جستجو")
    
    def save_settings(self):
        """ذخیره تنظیمات"""
        config.GOOGLE_CSE_ID = self.cse_id_input.text()
        config.GOOGLE_CSE_API_KEY = self.api_key_input.text()
        config.REQUEST_TIMEOUT = self.settings_timeout_spinbox.value()
        
        show_info(self, "موفقیت", "تنظیمات با موفقیت ذخیره شدند")
        self.statusbar.showMessage("تنظیمات ذخیره شدند")

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()