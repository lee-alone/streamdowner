from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, 
                                    QTableWidget, QTableWidgetItem, QPushButton,
                                    QLineEdit, QLabel)
from PySide6.QtCore import Qt
from datetime import datetime
import os

class HistoryDialog(QDialog):
    def __init__(self, history_manager, parent=None):
        super().__init__(parent)
        self.history_manager = history_manager
        self.setup_ui()
        self.load_history()
        
    def setup_ui(self):
        self.setWindowTitle("下载历史")
        self.setMinimumSize(600, 400)
        
        layout = QVBoxLayout(self)
        
        # 搜索区域
        search_layout = QHBoxLayout()
        search_label = QLabel("搜索:")
        self.search_input = QLineEdit()
        self.search_input.textChanged.connect(self.search_history)
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_input)
        layout.addLayout(search_layout)
        
        # 历史记录表格
        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["文件名", "URL", "保存路径", "时间", "状态"])
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        layout.addWidget(self.table)
        
        # 按钮区域
        button_layout = QHBoxLayout()
        clear_button = QPushButton("清空历史")
        clear_button.clicked.connect(self.clear_history)
        redownload_button = QPushButton("重新下载所选")
        redownload_button.clicked.connect(self.redownload_selected)
        button_layout.addWidget(clear_button)
        button_layout.addWidget(redownload_button)
        layout.addLayout(button_layout)
        
    def load_history(self, entries=None):
        if entries is None:
            entries = self.history_manager.get_recent_entries()
        self.table.setRowCount(len(entries))
        
        for row, entry in enumerate(entries):
            self.table.setItem(row, 0, QTableWidgetItem(entry['filename']))
            self.table.setItem(row, 1, QTableWidgetItem(entry['url']))
            self.table.setItem(row, 2, QTableWidgetItem(entry['save_path']))
            
            timestamp = datetime.fromisoformat(entry['timestamp'])
            time_str = timestamp.strftime("%Y-%m-%d %H:%M:%S")
            self.table.setItem(row, 3, QTableWidgetItem(time_str))
            self.table.setItem(row, 4, QTableWidgetItem(entry['status']))
            
    def search_history(self):
        keyword = self.search_input.text()
        if keyword:
            entries = self.history_manager.search_history(keyword)
        else:
            entries = self.history_manager.get_recent_entries()
            
        self.table.setRowCount(len(entries))
        self.load_history(entries)
        
    def clear_history(self):
        self.history_manager.clear_history()
        self.table.setRowCount(0)
        
    def redownload_selected(self):
        selected_rows = list(set(item.row() for item in self.table.selectedItems()))
        if not selected_rows:
            return
            
        for row in selected_rows:
            url = self.table.item(row, 1).text()
            save_path = self.table.item(row, 2).text()
            
            # 通过父窗口触发下载
            if hasattr(self.parent(), 'start_download_with_url'):
                self.parent().start_download_with_url(url, save_path)