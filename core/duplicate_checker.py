import os
from core.history_manager import HistoryManager
from PySide6.QtWidgets import QMessageBox

def check_duplicate_download(url: str, save_path: str, filename: str, history_manager: HistoryManager, parent):
    """
    检查 URL 是否已经存在于历史记录中，以及检查保存路径下是否已经存在同名的文件。

    Args:
        url: 下载的 URL。
        save_path: 保存路径。
        filename: 文件名。
        history_manager: HistoryManager 对象。
        parent: 父窗口。

    Returns:
        如果 URL 已经存在于历史记录中，或者保存路径下已经存在同名的文件，返回 True，否则返回 (False, filename)。
    """
    # 检查历史记录
    history_entries = history_manager.search_history(url)
    if history_entries:
        reply = QMessageBox.question(parent, "警告", "该视频已下载过，是否继续？",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.No:
            return True
        else:
            # 用户选择继续下载，但文件名未知，返回 None
            return False, None

    # 检查文件名
    file_path = os.path.join(save_path, filename)
    if os.path.exists(file_path):
        reply = QMessageBox.question(parent, "警告", "该文件已存在，是否覆盖？",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.No:
            return True
        else:
            # 用户选择继续下载，但文件名未知，返回 None
            return False, None

    return False, None