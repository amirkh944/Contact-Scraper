from PyQt6.QtWidgets import QMessageBox, QProgressDialog
from PyQt6.QtCore import Qt

def show_error(parent, title: str, message: str):
    """
    نمایش پنجره خطا
    
    Args:
        parent: عنصر والد
        title: عنوان پنجره
        message: پیام خطا
    """
    QMessageBox.critical(parent, title, message)

def show_warning(parent, title: str, message: str):
    """
    نمایش پنجره هشدار
    
    Args:
        parent: عنصر والد
        title: عنوان پنجره
        message: پیام هشدار
    """
    QMessageBox.warning(parent, title, message)

def show_info(parent, title: str, message: str):
    """
    نمایش پنجره اطلاعات
    
    Args:
        parent: عنصر والد
        title: عنوان پنجره
        message: پیام اطلاعات
    """
    QMessageBox.information(parent, title, message)

def show_question(parent, title: str, message: str) -> bool:
    """
    نمایش پنجره سوال
    
    Args:
        parent: عنصر والد
        title: عنوان پنجره
        message: متن سوال
        
    Returns:
        نتیجه انتخاب کاربر
    """
    reply = QMessageBox.question(
        parent, title, message,
        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
    )
    return reply == QMessageBox.StandardButton.Yes