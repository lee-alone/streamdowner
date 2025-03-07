from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                                    QLineEdit, QPushButton, QTabWidget, QLabel, 
                                    QProgressBar, QTableWidget, QTableWidgetItem,
                                    QFileDialog, QComboBox, QGroupBox, QCheckBox,
                                    QMessageBox, QStatusBar)
from PySide6.QtCore import Qt, QThread, Signal, QUrl
from PySide6.QtGui import QAction, QClipboard, QPalette, QColor
import os
from core.download_manager import DownloadManager
from core.history_manager import HistoryManager
from .history_dialog import HistoryDialog

class DownloadThread(QThread):
    def __init__(self, manager, url, save_path, options):
        super().__init__()
        self.manager = manager
        self.url = url
        self.save_path = save_path
        self.options = options

    def run(self):
        self.manager.download(self.url, self.save_path, self.options)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("老李没事锉一个下载器——九中内部使用版")
        self.setMinimumSize(800, 600)
        self.download_manager = DownloadManager()
        self.history_manager = HistoryManager()
        self.download_manager.progress_updated.connect(self.update_progress)
        self.download_manager.download_completed.connect(self.download_completed)
        self.download_manager.download_error.connect(self.download_error)
        self.download_manager.queue_updated.connect(self.update_queue_status)
        self.active_downloads = {}
        self.setup_ui()
        self.setup_menubar()
        self.setup_statusbar()
        self.setAcceptDrops(True)  # 启用拖放
        
    def setup_menubar(self):
        menubar = self.menuBar()
        
        # 文件菜单
        file_menu = menubar.addMenu("文件")
        history_action = QAction("下载历史", self)
        history_action.triggered.connect(self.show_history)
        settings_action = QAction("设置", self)
        file_menu.addActions([history_action, settings_action])
        
        # 主题菜单
        theme_menu = menubar.addMenu("主题")
        self.light_theme = QAction("明亮模式", self, checkable=True)
        self.dark_theme = QAction("暗黑模式", self, checkable=True)
        self.light_theme.setChecked(True)
        theme_menu.addActions([self.light_theme, self.dark_theme])
        
        self.light_theme.triggered.connect(lambda: self.switch_theme("light"))
        self.dark_theme.triggered.connect(lambda: self.switch_theme("dark"))
        
        # 帮助菜单
        help_menu = menubar.addMenu("帮助")
        about_action = QAction("关于", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def setup_statusbar(self):
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)
        self.queue_label = QLabel("队列: 0 | 活动: 0")
        self.statusBar.addWidget(self.queue_label)

    def switch_theme(self, theme):
        if theme == "dark":
            self.light_theme.setChecked(False)
            self.dark_theme.setChecked(True)
            self.set_dark_theme()
        else:
            self.light_theme.setChecked(True)
            self.dark_theme.setChecked(False)
            self.set_light_theme()

    def set_dark_theme(self):
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(53, 53, 53))
        palette.setColor(QPalette.WindowText, QColor(255, 255, 255))
        palette.setColor(QPalette.Base, QColor(35, 35, 35))
        palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
        palette.setColor(QPalette.ToolTipBase, QColor(255, 255, 255))
        palette.setColor(QPalette.ToolTipText, QColor(255, 255, 255))
        palette.setColor(QPalette.Text, QColor(255, 255, 255))
        palette.setColor(QPalette.Button, QColor(53, 53, 53))
        palette.setColor(QPalette.ButtonText, QColor(255, 255, 255))
        palette.setColor(QPalette.BrightText, QColor(255, 0, 0))
        palette.setColor(QPalette.Link, QColor(42, 130, 218))
        palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
        palette.setColor(QPalette.HighlightedText, QColor(255, 255, 255))
        self.setPalette(palette)
        
    def set_light_theme(self):
        self.setPalette(self.style().standardPalette())

    def setup_ui(self):
        # 创建中心窗口部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # URL输入区域
        url_layout = QHBoxLayout()
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("在此输入视频URL...")
        paste_button = QPushButton("粘贴")
        paste_button.clicked.connect(self.paste_url)
        url_layout.addWidget(self.url_input)
        url_layout.addWidget(paste_button)
        main_layout.addLayout(url_layout)
        
        # 选项卡区域
        tabs = QTabWidget()
        tabs.addTab(self.create_basic_tab(), "基本选项")
        tabs.addTab(self.create_advanced_tab(), "高级选项")
        main_layout.addWidget(tabs)
        
        # 下载按钮
        download_button = QPushButton("开始下载")
        download_button.setStyleSheet("QPushButton { padding: 10px; font-size: 16px; }")
        download_button.clicked.connect(self.start_download)
        main_layout.addWidget(download_button)
        
        # 下载任务列表
        self.tasks_table = QTableWidget(0, 4)
        self.tasks_table.setHorizontalHeaderLabels(["文件名", "进度", "速度", "状态"])
        main_layout.addWidget(self.tasks_table)
        
    def create_basic_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 下载类型选择
        type_group = QGroupBox("下载类型")
        type_layout = QHBoxLayout()
        self.download_type = QComboBox()
        self.download_type.addItems(["视频", "音频", "播放列表"])
        type_layout.addWidget(self.download_type)
        type_group.setLayout(type_layout)
        layout.addWidget(type_group)
        
        # 保存路径选择
        path_group = QGroupBox("保存路径")
        path_layout = QHBoxLayout()
        self.path_input = QLineEdit()
        self.path_input.setReadOnly(True)
        browse_button = QPushButton("浏览...")
        browse_button.clicked.connect(self.choose_save_path)
        path_layout.addWidget(self.path_input)
        path_layout.addWidget(browse_button)
        path_group.setLayout(path_layout)
        layout.addWidget(path_group)
        
        return widget
        
    def create_advanced_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # 视频质量选择
        quality_group = QGroupBox("视频质量")
        quality_layout = QVBoxLayout()
        self.quality_combo = QComboBox()
        self.quality_combo.addItems(["最佳质量", "1080p", "720p", "480p", "360p"])
        quality_layout.addWidget(self.quality_combo)
        quality_group.setLayout(quality_layout)
        layout.addWidget(quality_group)
        
        # 格式选择
        format_group = QGroupBox("格式选择")
        format_layout = QVBoxLayout()
        self.format_combo = QComboBox()
        self.format_combo.addItems(["mp4", "mkv", "webm", "mp3", "m4a", "flac"])
        format_layout.addWidget(self.format_combo)
        format_group.setLayout(format_layout)
        layout.addWidget(format_group)
        
        # 音频选项
        audio_group = QGroupBox("音频选项")
        audio_layout = QVBoxLayout()
        self.include_audio_check = QCheckBox("下载视频时包含音频")
        self.include_audio_check.setChecked(True)  # 默认勾选
        audio_layout.addWidget(self.include_audio_check)
        audio_group.setLayout(audio_layout)
        layout.addWidget(audio_group)
        
        # 字幕选项
        subtitle_group = QGroupBox("字幕选项")
        subtitle_layout = QVBoxLayout()
        self.subtitle_check = QCheckBox("下载字幕")
        subtitle_layout.addWidget(self.subtitle_check)
        subtitle_group.setLayout(subtitle_layout)
        layout.addWidget(subtitle_group)
        
        return widget

    def paste_url(self):
        clipboard = QApplication.clipboard()
        self.url_input.setText(clipboard.text())

    def choose_save_path(self):
        path = QFileDialog.getExistingDirectory(self, "选择保存路径")
        if path:
            self.path_input.setText(path)

    def start_download(self):
        url = self.url_input.text().strip()
        if not url:
            QMessageBox.warning(self, "错误", "请输入URL")
            return

        save_path = self.path_input.text()
        if not save_path:
            save_path = os.path.expanduser("~/Downloads")
            self.path_input.setText(save_path)

        options = {
            'download_type': self.download_type.currentText(),
            'quality': self.quality_combo.currentText(),
            'format': self.format_combo.currentText(),
            'subtitle_enabled': self.subtitle_check.isChecked(),
            'include_audio': self.include_audio_check.isChecked()  # 添加新选项
        }

        # Add new row to tasks table
        row = self.tasks_table.rowCount()
        self.tasks_table.insertRow(row)
        self.tasks_table.setItem(row, 0, QTableWidgetItem(url))
        progress_bar = QProgressBar()
        self.tasks_table.setCellWidget(row, 1, progress_bar)
        self.tasks_table.setItem(row, 2, QTableWidgetItem("队列中..."))
        self.tasks_table.setItem(row, 3, QTableWidgetItem("等待中"))

        # Store row information
        self.active_downloads[url] = {
            'row': row,
            'progress_bar': progress_bar
        }

        # Add to download queue
        self.download_manager.add_download(url, save_path, options)
        
        # Clear URL input
        self.url_input.clear()

    def update_progress(self, url, progress):
        if url in self.active_downloads:
            download = self.active_downloads[url]
            row = download['row']
            progress_bar = download['progress_bar']
            
            self.tasks_table.setItem(row, 0, QTableWidgetItem(progress.filename))
            progress_bar.setValue(int(progress.percent))
            self.tasks_table.setItem(row, 2, QTableWidgetItem(progress.speed))
            self.tasks_table.setItem(row, 3, QTableWidgetItem(progress.status))

    def show_history(self):
        dialog = HistoryDialog(self.history_manager, self)
        dialog.exec()

    def start_download_with_url(self, url: str, save_path: str = None):
        """从历史记录中重新下载"""
        self.url_input.setText(url)
        if save_path:
            self.path_input.setText(save_path)
        self.start_download()

    def download_completed(self, url):
        if url in self.active_downloads:
            download = self.active_downloads[url]
            row = download['row']
            self.tasks_table.setItem(row, 2, QTableWidgetItem("-"))
            self.tasks_table.setItem(row, 3, QTableWidgetItem("已完成"))
            
            # 添加到历史记录
            filename = self.tasks_table.item(row, 0).text()
            save_path = self.path_input.text()
            options = {
                'download_type': self.download_type.currentText(),
                'quality': self.quality_combo.currentText(),
                'format': self.format_combo.currentText(),
                'subtitle_enabled': self.subtitle_check.isChecked()
            }
            self.history_manager.add_entry(url, filename, save_path, options)

    def download_error(self, url, error):
        if url in self.active_downloads:
            download = self.active_downloads[url]
            row = download['row']
            self.tasks_table.setItem(row, 2, QTableWidgetItem("-"))
            self.tasks_table.setItem(row, 3, QTableWidgetItem(f"错误: {error}"))

    def update_queue_status(self, queue_size: int, active_count: int):
        self.queue_label.setText(f"队列: {queue_size} | 活动: {active_count}")

    def dragEnterEvent(self, event):
        """处理拖入事件"""
        if event.mimeData().hasUrls() or event.mimeData().hasText():
            event.acceptProposedAction()

    def dropEvent(self, event):
        """处理放下事件"""
        mime_data = event.mimeData()
        
        if mime_data.hasUrls():
            for url in mime_data.urls():
                text = url.toString()
                if any(service in text.lower() for service in ['youtube.com', 'youtu.be', 'bilibili.com']):
                    self.url_input.setText(text)
                    self.start_download()
                    break
        elif mime_data.hasText():
            text = mime_data.text()
            if any(service in text.lower() for service in ['youtube.com', 'youtu.be', 'bilibili.com']):
                self.url_input.setText(text)
                self.start_download()

    def dragMoveEvent(self, event):
        """处理拖动移动事件"""
        event.acceptProposedAction()

    def show_about(self):
        QMessageBox.information(self, "关于", "九中专用版，出错找老李修复")